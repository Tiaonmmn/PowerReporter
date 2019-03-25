import os
import datetime
from loguru import logger
from Registry import Registry


class customShellFolder:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def getCustomShellFolder(self):
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
                    open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
                except Registry.RegistryKeyNotFoundException:
                    logger.error("Couldn't find UserAssist registry on user {0}".format(userDir))
                    continue
                logger.info("Now showing %s User Shell Folders info!" % userDir)

                for item in open1.values():
                    tempResult = dict()
                    logger.info("{0:20} : {1}".format(item.name(), item.value()))
                    tempResult[item.name()] = item.value()
                    result.append(tempResult)
        logger.critical(result)
        return result

    def getCustomShellFolderByUserName(self, userName):
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
                if userName == userDir:
                    if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                    elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                    else:
                        logger.warning("Couldn't find user registry on %s" % userDir)
                        continue
                    try:
                        open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
                    except Registry.RegistryKeyNotFoundException:
                        logger.error("Couldn't find UserAssist registry on user {0}".format(userDir))
                        continue
                    logger.info("Now showing %s User Shell Folders info!" % userDir)
                    tempResult = dict()
                    for item in open1.values():
                        tempResult[item.name()] = item.value()
                        result.append(tempResult)
                else:
                    continue
        return result
