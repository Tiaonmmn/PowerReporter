__author__ = "Tiaonmmn.ZMZ"
import os
from Registry import Registry
from loguru import logger
import subprocess
import glob
from thirdParty import prefetch
import datetime
import codecs
from thirdParty import userAssist


class applicationExecutionLog:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def getPrefetchFile(self):
        output = self.volumeInfo
        result = []
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/Windows/Prefetch" % (self.mountDir, output.split(" ")[2]))
            for line in glob.iglob(r"*.pf"):
                result.append(line)
        return result

    def showAllPrefetchFileInfo(self) -> dict:
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            for line in glob.iglob(r"Windows/Prefetch/*.pf"):
                if os.path.getsize(line) > 0:
                    self.parsePrefetchFileInfo(line)

    def parsePrefetchFileInfo(self, inputFile) -> dict:
        p = prefetch.Prefetch(infile=inputFile)
        logger.info("{0:25} : {1}".format("Executable Name", p.executableName.decode()))
        logger.info("{0:25} : {1}".format("Run Counts", p.runCount))
        if len(p.timestamps) > 1:
            for i in p.timestamps:
                logger.info("{0:25} : {1}".format("Last Executed", i))
        else:
            logger.info("{0:25} : {1}".format("Last Executed", p.timestamps[0]))

        logger.debug("{0:25}".format("Volume Info"))
        for i in p.volumesInformationArray:
            logger.info("{0:25} : {1}".format("Volume Name", i["Volume Name"].decode()))
            logger.info("{0:25} : {1}".format("Creation Date", i["Creation Date"]))
            logger.info("{0:25} : {1}".format("Serial Number", i["Serial Number"]))
        logger.debug("{0:25}".format("Directory Strings:"))
        for volume in p.directoryStringsArray:
            for i in volume:
                logger.info("    " + i.decode())
        logger.debug("{0:25}".format("Resources loaded:"))
        count = 1
        for i in p.resources:
            i = i.decode()
            if i:
                if count > 999:
                    logger.info("{}: {}".format(count, i))
                if count > 99:
                    logger.info("{}:  {}".format(count, i))
                elif count > 9:
                    logger.info("{}:   {}".format(count, i))
                else:
                    logger.info("{}:    {}".format(count, i))
            count += 1

    def getLastExecutionByPrefetch(self):
        output = self.volumeInfo
        result = dict()
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.warning("The partition may not be accurate!Please aware it!!!!!")

            for line in glob.iglob(r"Windows/Prefetch/*.pf"):
                if os.path.getsize(line) > 0:
                    p = prefetch.Prefetch(infile=line)
                    p.timestamps[-1] = (
                            datetime.datetime.strptime(p.timestamps[-1], "%Y %m %d - %H:%M:%S") + bias).strftime(
                        "%Y %m %d - %H:%M:%S")

                    for resourceName in p.resources:  # resourceName is a byte
                        tempName = p.executableName.decode().upper()
                        if tempName in resourceName.decode():
                            if (resourceName.decode())[-4:len(resourceName.decode())] == ".EXE":
                                tempPathName = resourceName.decode()
                                mayUsed = tempPathName.split("\\")
                                realPathName = ""
                                if mayUsed[0] == '' and mayUsed[1] == 'DEVICE' and "HARDDISKVOLUME" in mayUsed[2]:
                                    realPathName = "C:\\"
                                for i in range(len(mayUsed) - 3):
                                    realPathName += mayUsed[i + 3] + "\\"
                                # realPathName=realPathName[:-1].replace("\\\\","|")
                                realPathName = realPathName[:-1]

                                result[realPathName] = p.timestamps[-1]  # We need to manually get full executable path
                            else:
                                result[p.executableName.decode()] = p.timestamps[-1]
        logger.error(result)
        return result

    def parse_shimCacheParser_Output(self):
        '''https://medium.com/@bromiley/windows-wednesday-shim-cache-1997ba8b13e7'''
        output = self.volumeInfo
        result = dict()
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/system", os.F_OK | os.R_OK):
                parser_output = subprocess.getoutput(
                    "python2 {0} {1} {2}".format(
                        (os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shimCacheParser.py"), "-i",
                        "Windows/System32/config/system"))
            elif os.access("Windows/System32/config/SYSTEM", os.F_OK | os.R_OK):
                parser_output = subprocess.getoutput(
                    "python2 {0} {1} {2}".format(
                        (os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shimCacheParser.py"), "-i",
                        "Windows/System32/config/SYSTEM"))
            else:
                logger.warning("Couldn't find SYSTEM registry file!")
                return None
            for lines in parser_output.splitlines():
                logger.warning(lines)
                if "Last Modified Last Update Path File Size Exec Flag" in lines:
                    continue
                date = lines.split(" ")[0] + " " + lines.split(" ")[1] + " " + lines.split(" ")[2] + " "
                time = lines.split(" ")[4]  # not biased
                executableName = lines.split(" ")[-3]
                logger.warning("date:{0} time:{1} exe:{2}".format(date, time, executableName))
                runTime = datetime.datetime.strptime(date + "- " + time, "%Y %m %d - %H:%M:%S") + bias

                result[executableName] = runTime.strftime("%Y %m %d - %H:%M:%S")
        logger.error(result)
        return result

    def getUserAssistInfo(self):
        output = self.volumeInfo
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        result = dict()
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                try:
                    open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist")
                except Registry.RegistryKeyNotFoundException:
                    logger.error("Couldn't find UserAssist registry on user {0}".format(userDir))
                    continue
                for subkey in open1.subkeys():
                    count = subkey.subkey("Count")
                    for items in count.values():
                        logger.error(codecs.encode(items.name(), 'rot13'))
                        result[codecs.decode(items.name(), 'rot13') + " ----- %s" % userDir] = \
                            (datetime.datetime.strptime(userAssist.UserAssist(items.value()).as_dict()[
                                                            'last_execution'], "%Y %m %d - %H:%M:%S") + bias).strftime(
                                "%Y %m %d - %H:%M:%S")

        logger.error(result)
        return result
