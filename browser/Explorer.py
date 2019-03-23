import datetime
import os

from Registry import Registry
from loguru import logger


class Explorer:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def getKeyWordAtSearchbar(self):
        output = self.volumeInfo
        result = []
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
                    open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\WordWheelQuery")
                except Registry.RegistryKeyNotFoundException:
                    logger.error("Couldn't find UserAssist registry on user {0}".format(userDir))
                    continue
                logger.info("Now showing Windows Explorer searchbar info!")
                logger.info("Timestamp: " + (open1.timestamp() + bias).strftime('%Y %m %d - %H:%M:%S'))
                for item in open1.values():
                    if item.name() == 'MRUListEx':
                        continue
                    logger.info("KeyWords: %s" % (item.value().decode('utf-16-le')))
        logger.critical(result)
        return result

    def getRunMRU(self):
        output = self.volumeInfo
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
                open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU")
                networkIP = []
                logger.info("Showing Run MRU info.")
                for item in open1.values():
                    if item.name() == "MRUList":
                        continue
                    logger.info(open1.value())
                    if "\\\\" in open1.value():
                        networkIP.append(open1.value())
                logger.info("Last run time:" + (open1.timestamp() + bias).strftime("%Y %m %d - %H:%M:%S"))
        logger.critical("Found suspected network drive.%s" % networkIP)

    def getMapNetworkDriveMRU(self):

        output = self.volumeInfo
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
                open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Map Network Drive MRU")
                logger.info("Showing Map Network Drive MRU info.")
                for item in open1.values():
                    if item.name() == "MRUList":
                        continue
                    logger.info(open1.value())
    # https://digital-forensics.sans.org/blog/2011/07/05/shellbags
