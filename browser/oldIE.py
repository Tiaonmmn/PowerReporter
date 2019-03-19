from Registry import Registry
import os
import subprocess
import csv
import glob
import binascii
import datetime
from loguru import logger
import urllib


class IE:

    def __init__(self, volumeInfo, mountDir, tempDir, osVersion):
        self._userList = []
        self.volumeInfo = volumeInfo
        self.mountDir = mountDir
        self.IEVersion = self.getIEVersion()
        self.tempDir = tempDir
        self.osVersion = osVersion
        pass

    def getIEVersion(self):
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/software", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/software")
            elif os.access("Windows/System32/config/SOFTWARE", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SOFTWARE")
            else:
                logger.warning("Couldn't find SOFTWARE registry file!")
                return None
            IEVersion = registry.open("Microsoft\\Internet Explorer")
            logger.debug("Now listing Windows IE Version Information using registry!")
            if "svcVersion" in IEVersion.values():
                logger.info("Internet Explorer Version:     " + IEVersion.value("svcVersion").value())
                return IEVersion.value("svcVersion").value()
            else:
                logger.info("Internet Explorer Version:     " + IEVersion.value("Version").value())
                return IEVersion.value("Version").value()

    def getTypedURL(self):
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) < 10:
            output = self.volumeInfo
            if "FAT" or "NTFS" in output.split(" ")[0]:
                os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
                logger.info("Loading every user info!")  # TODO:It should be per user!
                try:
                    os.chdir("Users/")
                except FileNotFoundError:
                    logger.error("Couldn't find Users folder!")
                    return None
                for userDir in os.listdir("."):
                    self._userList.append(userDir)
                    if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                    elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                    else:
                        logger.warning("Couldn't find user registry on %s" % userDir)
                        continue
                    try:
                        typed = registry.open("Software\\Microsoft\\Internet Explorer\\TypedURLS")
                    except Registry.RegistryKeyNotFoundException:
                        logger.error("Couldn't find IE TypedURLS registry on user {0}".format(userDir))
                        continue
                    logger.info("Showing TypedURL info.")
                    for items in typed.values():
                        logger.info("{0:10}: {1}".format(items.name(), items.value()))

    def getIEHistory(self):
        result = []
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) < 10:
            output = self.volumeInfo
            if "FAT" or "NTFS" in output.split(" ")[0]:
                os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
                logger.info("Loading every user info!")  # TODO:It should be per user!
                try:
                    os.chdir("Users/")
                except FileNotFoundError:
                    logger.error("Couldn't find Users folder!")
                    return None
                for userDir in self._userList:
                    if ("Windows XP" or "Windows 2000") in self.osVersion:
                        try:
                            temp = glob.glob(
                                "../Documents and Settings/" + userDir + "/Local Settings/History/History.IE5/" + "/*.dat")[0]
                        except IndexError:
                            continue
                        if os.access(temp, os.F_OK | os.R_OK):
                            filePath = os.path.realpath(temp)
                        else:
                            logger.critical("Couldn't find Index.dat file on %s.Please aware it." % temp)
                            return None
                    else:
                        try:
                            temp = glob.glob(
                                userDir + "/AppData/Local/Microsoft/Windows/History/History.IE5/" + "/*.dat")[0]
                            logger.error(temp)
                        except IndexError:
                            logger.critical("Not in Win7.")
                            continue
                        if os.access(temp, os.F_OK | os.R_OK):
                            filePath = os.path.realpath(temp)
                        else:
                            logger.critical("Couldn't find Index.dat file on %s.Please aware it." % temp)
                            return None
                    logger.info("Now showing History Index.dat file %s info." % filePath)
                    logger.debug(subprocess.getoutput("msiecfinfo -v -a " + filePath))
                    logger.info("Now parsing History Index.dat file.")
                    output = subprocess.getoutput("pasco -d " + filePath)
                    logger.debug(output)
                    output = output.splitlines()[1:]
                    output = "\n".join(output)
                    logger.debug(output)
                    reader = csv.reader(output[1], delimiter='\t')
                    for line in reader:  # 0:TYPE,1:URL,2:MODIFIED TIME,3:ACCESS TIME,4:FILENAME,5:DIRECTORY,6:HTTP HEADERS
                        if line[0] == "TYPE":
                            continue
                        tempResult = dict()
                        logger.error(line)
                        logger.info("{0:15} : {1}".format("URL", line[1]))
                        logger.info("{0:15} : {1}".format("Modified Time", line[2]))
                        logger.info("{0:15} : {1}".format("Access Time", line[3]))
                        tempResult['URL'] = line[1]
                        tempResult['Access Time'] = datetime.datetime.strptime(line[3].split(".")[0],
                                                                               "%m/%d/%Y %H:%M:%S").strftime(
                            "%Y %m %d - %H:%M:%S")
                        result.append(tempResult)
        logger.critical(result)
        return result
