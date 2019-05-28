import csv
import datetime
import glob
import os
import subprocess

from Registry import Registry
from loguru import logger


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
                                "../Documents and Settings/" + userDir + "/Local Settings/History/History.IE5/" + "/*.dat")[
                                0]
                        except IndexError:
                            continue
                        if os.access(temp, os.F_OK | os.R_OK):
                            filePath = os.path.realpath(temp)
                        else:
                            logger.critical("Couldn't find Index.dat file on %s.Please aware it." % temp)
                            continue
                    else:
                        try:
                            temp = glob.glob(
                                userDir + "/AppData/Local/Microsoft/Windows/History/History.IE5/" + "/*.dat")[0]
                        except IndexError:
                            logger.critical("Couldn't find historyFolder %s index.dat" % (
                                    userDir + "/AppData/Local/Microsoft/Windows/History/History.IE5/"))
                            continue
                        if os.access(temp, os.F_OK | os.R_OK):
                            filePath = os.path.realpath(temp)
                        else:
                            logger.critical("Couldn't find Index.dat file on %s.Please aware it." % temp)
                            continue
                    logger.info("Now showing History Index.dat file %s info." % filePath)
                    logger.debug(subprocess.getoutput("msiecfinfo -v -a " + filePath))
                    logger.info("Now parsing History Index.dat file.")
                    output = subprocess.getoutput("pasco -d " + filePath)
                    logger.debug(output)
                    output = output.splitlines()
                    reader = csv.reader(output[2:], delimiter='\t', quotechar="\n")
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

        return result

    def getIEContents(self):
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

                    if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                    elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                    else:
                        logger.warning("Couldn't find user registry on %s" % "{0}/ntuser.dat".format(userDir))
                        continue
                    try:
                        shellFolder = registry.open(
                            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
                    except Registry.RegistryKeyNotFoundException:
                        logger.critical("Couldn't find User Shell Folders key!")
                        continue

                    if ("Windows XP" or "Windows 2000") in self.osVersion:
                        cacheFolder = shellFolder.value("Cache").value().replace("%USERPROFILE%",
                                                                                 os.getcwd() + "/" + userDir)
                        try:
                            temp = glob.glob(
                                "../Documents and Settings/" + userDir + "/Local Settings/History/History.IE5/" + "/*.dat")[
                                0]
                        except IndexError:
                            continue
                        if os.access(temp, os.F_OK | os.R_OK):
                            filePath = os.path.realpath(temp)
                        else:
                            logger.critical("Couldn't find Index.dat file on %s.Please aware it." % temp)
                            continue
                    else:
                        cacheFolder = shellFolder.value("Cache").value().replace("%USERPROFILE%",
                                                                                 os.getcwd() + "/" + userDir).replace(
                            "\\", "/")
                        if os.access(cacheFolder, os.F_OK | os.R_OK):
                            pass
                        else:
                            logger.critical("Couldn't find cacheFolder on %s.Please aware it." % cacheFolder)
                            continue
                        try:
                            filePath = glob.glob(cacheFolder + "/Content.IE5/" + "*.dat")[0]
                        except IndexError:
                            logger.critical("Couldn't find cacheFolder %s index.dat." % cacheFolder)
                            continue
                        if os.access(filePath, os.R_OK | os.F_OK):
                            pass
                        else:
                            logger.critical("Couldn't find Content Index.dat file on %s!" % os.getcwd() + filePath)
                    logger.info("Now showing Content Index.dat file %s info." % filePath)
                    logger.debug(subprocess.getoutput("msiecfinfo -v -a '%s' " % filePath))
                    logger.info("Now parsing Contents Index.dat file.")
                    # output = subprocess.getoutput("pasco '%s' " % filePath)
                    # logger.debug(output)
                    # output = output.splitlines()
                    # reader = csv.reader(output[2:], delimiter='\t', quotechar="\n")
                    # for line in reader:  # 0:TYPE,1:URL,2:MODIFIED TIME,3:ACCESS TIME,4:FILENAME,5:DIRECTORY,6:HTTP HEADERS
                    #     if line[0] == "TYPE":
                    #         continue
                    #     tempResult = dict()
                    #     logger.info("{0:15} : {1}".format("URL", line[1]))
                    #     logger.info("{0:15} : {1}".format("Modified Time", line[2]))
                    #     logger.info("{0:15} : {1}".format("Access Time", line[3]))
                    #     logger.info("{0:15} : {1}".format("Filename", line[4]))
                    #     logger.info("{0:15} : {1}".format("Directory", line[5]))
                    #     logger.info("{0:15} : {1}".format("HTTP Headers", line[6]))
                    #     tempResult['URL'] = line[1]
                    #     try:
                    #         tempResult['Access Time'] = datetime.datetime.strptime(line[3].split(".")[0],
                    #                                                                "%m/%d/%Y %H:%M:%S").strftime(
                    #             "%Y %m %d - %H:%M:%S")
                    #     except ValueError:
                    #         tempResult['Access Time'] = line[3]
                    #     result.append(tempResult)
                    output = subprocess.getoutput("msiecfexport -m all '%s'" % filePath)
                    logger.debug(output)
                    output = output.splitlines()[5:-1]
                    count = 0
                    while True:
                        if "Record type" in output[count] and "URL" in output[count]:  # count=0
                            logger.info("{0:20} : {1}".format("Record type", output[count][15:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Offset range", output[count][16:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Location", output[count][12:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Primary time", output[count][16:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Last checked time", output[count][21:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Filename", output[count][12]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Cache directory name", output[count][24:]))
                            count += 1
                            logger.info("")
                        if "Record type" in output[count] and "REDR" in output[count]:  # count=0
                            logger.info("{0:20} : {1}".format("Record type", output[count][15:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Offset range", output[count][16:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Location", output[count][12:]))
                            count += 1
                            logger.info("")
                        if "Record type" in output[count] and "LEAK" in output[count]:  # count=0
                            logger.info("{0:20} : {1}".format("Record type", output[count][15:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Offset range", output[count][16:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Filename", output[count][12:]))
                            count += 1
                            logger.info("{0:20} : {1}".format("Cache directory index", output[count][25:]))
                            count += 1
                            logger.info("")
                        count += 1
                        if count == len(output):
                            break

        # logger.critical(result)
        # return result

    def getIECookies(self):
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
                    if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                    elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                    else:
                        logger.warning("Couldn't find user registry on %s" % userDir)
                        continue
                    try:
                        shellFolder = registry.open(
                            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
                    except Registry.RegistryKeyNotFoundException:
                        logger.critical("Couldn't find User Shell Folders key!")
                        continue

                    if ("Windows XP" or "Windows 2000") in self.osVersion:
                        cookiesFolder = shellFolder.value("Cookies").value().replace("%USERPROFILE%",
                                                                                     os.getcwd() + "/" + userDir)
                        try:
                            temp = glob.glob(
                                "../Documents and Settings/" + userDir + "/Local Settings/History/History.IE5/" + "/*.dat")[
                                0]
                        except IndexError:
                            continue
                        if os.access(temp, os.F_OK | os.R_OK):
                            filePath = os.path.realpath(temp)
                        else:
                            logger.critical("Couldn't find Index.dat file on %s.Please aware it." % temp)
                            continue
                    else:
                        cookiesFolder = shellFolder.value("Cookies").value().replace("%USERPROFILE%",
                                                                                     os.getcwd() + "/" + userDir).replace(
                            "\\",
                            "/")
                        if os.access(cookiesFolder, os.F_OK | os.R_OK):
                            pass
                        else:
                            logger.critical("Couldn't find cookiesFolder on %s.Please aware it." % cookiesFolder)
                            continue
                        try:
                            filePath = (glob.glob(cookiesFolder + "/*.dat")[0])
                        except IndexError:
                            logger.critical("Couldn't find cookiesFolder %s index.dat." % cookiesFolder)
                            continue
                        if os.access(filePath, os.R_OK | os.F_OK):
                            pass
                        else:
                            logger.critical("Couldn't find Cookies Index.dat file on %s!" % os.getcwd() + filePath)
                    logger.info("Now showing Cookies Index.dat file %s info." % filePath)
                    logger.debug(subprocess.getoutput("msiecfinfo -v -a " + filePath))
                    logger.info("Now parsing Cookies Index.dat file.")
                    output = subprocess.getoutput("pasco -d " + filePath)
                    logger.debug(output)
                    output = output.splitlines()
                    reader = csv.reader(output[2:], delimiter='\t', quotechar="\n")
                    for line in reader:  # 0:TYPE,1:URL,2:MODIFIED TIME,3:ACCESS TIME,4:FILENAME,5:DIRECTORY,6:HTTP HEADERS
                        if line[0] == "TYPE":
                            continue
                        tempResult = dict()
                        logger.error(line)
                        logger.info("{0:15} : {1}".format("URL", line[1]))
                        logger.info("{0:15} : {1}".format("Modified Time", line[2]))
                        logger.info("{0:15} : {1}".format("Access Time", line[3]))
                        logger.info("{0:15} : {1}".format("Filename", line[4]))
                        try:
                            logger.info("{0:15} : {1}".format("Cookies contents", open(line[4]).read()))
                        except FileNotFoundError:
                            pass
                        tempResult['URL'] = line[1]
                        tempResult['Access Time'] = datetime.datetime.strptime(line[3].split(".")[0],
                                                                               "%m/%d/%Y %H:%M:%S").strftime(
                            "%Y %m %d - %H:%M:%S")
                        result.append(tempResult)

        return result
