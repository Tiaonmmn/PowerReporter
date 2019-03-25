import os
import subprocess
import datetime
import magic
from Registry import Registry
from loguru import logger


class Office:
    def __init__(self, mountDir: str, volumeInfo: str, bias, tempDir):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias
        self.tempDir = tempDir
        self._outlookVersions = self.getOutlookVersion()
        self._outlookDatabases = self.parsePath()

    def getOutlookVersion(self):
        result = []
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/software", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/software")
            elif os.access("Windows/System32/config/SOFTWARE", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SOFTWARE")
            else:
                logger.warning("Couldn't find SOFTWARE registry file!")
                return None
            try:
                open1 = registry.open("Microsoft\\Office")
            except Registry.RegistryKeyNotFoundException:
                logger.critical("Couldn't find Office install registry!")
                return None
            try:
                for version in open1.subkeys():
                    try:
                        if version.subkey("Outlook").subkey("Setup") is not None:
                            result.append(version.name())
                    except Registry.RegistryKeyNotFoundException:
                        continue
            except Registry.RegistryKeyNotFoundException:
                logger.critical("Couldn't find Outlook install version registry!")
                return None
        logger.info("Outlook installed versions: %s" % result)
        return result

    def locateOSTFile(self):
        output = self.volumeInfo
        result = []
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
                    open1 = registry.open("Software\\Microsoft\\Office")
                except Registry.RegistryKeyNotFoundException:
                    logger.critical("Couldn't find Office install registry on user {0}".format(userDir))
                    continue
                logger.info('Now showing Outlook database info.')
                for version in self._outlookVersions:
                    try:
                        open2 = open1.subkey(version).subkey("Outlook").subkey("Search")
                    except Registry.RegistryKeyNotFoundException:
                        continue
                    for item in open2.values():
                        logger.info(item.name())
                        result.append(item.name())

        logger.critical(result)
        return result

    def parsePath(self):
        temp = self.locateOSTFile()
        if temp is None:
            return None

        result = []
        for tempLine in temp:
            tempLine = tempLine.split("\\")
            tempLine[0] = "%s/%s/" % (self.mountDir, self.volumeInfo.split(" ")[2])
            result.append('/'.join(tempLine))
        logger.critical(result)
        return result

    def showMessage(self):
        logger.info("Now showing Outlook OST info.")
        os.chdir(self.tempDir)
        if self._outlookDatabases is None:
            return None
        for database in self._outlookDatabases:
            logger.debug(subprocess.getoutput("pffinfo -a -v " + database))
        logger.info("Now showing Outlook Message info.")
        try:
            os.mkdir("mails")
        except FileExistsError:
            pass
        os.chdir("mails")
        for database in self._outlookDatabases:
            logger.debug(subprocess.getoutput("pffexport -m all -v " + database))

        for dir_path, subpaths, files in os.walk("."):
            if subpaths == [] and files == []:  # dir_path is a directory.
                pass
            if subpaths == [] and ("txt" in i for i in files) and files != []:  # Found message.
                logger.info("Now showing message files location.")
                logger.debug(subprocess.getoutput("ls -la '%s'" % dir_path))

    def getOfficeFileMRU(self):
        output = self.volumeInfo
        result = []
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))

            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                logger.info("Loading user %s info!" % userDir)  # TODO:It should be per user!
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                try:
                    open1 = registry.open("Software\\Microsoft\\Office")
                except Registry.RegistryKeyNotFoundException:
                    logger.critical("Couldn't find Office install registry on user {0}".format(userDir))
                    continue
                for version in self._outlookVersions:
                    try:
                        open2 = open1.subkey(version)
                    except Registry.RegistryKeyNotFoundException as e:
                        logger.critical(e)
                        continue

                    for component in open2.subkeys():
                        try:
                            open3 = component.subkey("File MRU")
                        except Exception as e:
                            logger.critical(e)
                            continue
                        logger.info("Now showing %s File MRU" % component.name())
                        for item in open3.values():
                            logger.info("{0} : {1}".format(item.name(), item.value()))

        logger.critical(result)
        return result

    def getOfficePlaceMRU(self):
        output = self.volumeInfo
        result = []
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))

            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                logger.info("Loading user %s info!" % userDir)  # TODO:It should be per user!
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                try:
                    open1 = registry.open("Software\\Microsoft\\Office")
                except Registry.RegistryKeyNotFoundException:
                    logger.critical("Couldn't find Office install registry on user {0}".format(userDir))
                    continue
                for version in self._outlookVersions:
                    try:
                        open2 = open1.subkey(version)
                    except Registry.RegistryKeyNotFoundException as e:
                        logger.critical(e)
                        continue

                    for component in open2.subkeys():
                        try:
                            open3 = component.subkey("Place MRU")
                        except Exception as e:
                            logger.critical(e)
                            continue
                        logger.info("Now showing %s Place MRU" % component.name())
                        for item in open3.values():
                            logger.info("{0} : {1}".format(item.name(), item.value()))

        logger.critical(result)
        return result

    def getOfficeRecentLNKInfo(self):
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if os.access("{0}/AppData/Roaming/Microsoft/Office/Recent/".format(userDir),
                             os.F_OK | os.R_OK):
                    fileList = os.listdir("{0}/AppData/Roaming/Microsoft/Office/Recent/".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                fileList = ["{0}/AppData/Roaming/Microsoft/Office/Recent/".format(userDir) + a for a in
                            fileList]
                for file in fileList:
                    if os.path.isdir(file):
                        continue
                    logger.info("Now showing Office Recent lnk file %s info!" % file)
                    logger.debug(subprocess.getoutput(
                        "python2 {0} '{1}'".format(os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/lnkparse.py",
                                                   file)))
