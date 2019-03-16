from Registry import Registry
import os
import glob
from loguru import logger


class Chrome:
    def __init__(self, volumeInfo, mountDir):
        self.volumeInfo = volumeInfo
        self.mountDir = mountDir
        pass

    def getChromeVersion(self):
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
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                try:
                    open1 = registry.open("Software\\Google\\Chrome\\BLBeacon")
                except Registry.RegistryKeyNotFoundException:
                    logger.error("Couldn't find Google Chrome BLBeacon registry on user {0}".format(userDir))
                    continue
                logger.debug("Now listing Google Chrome version using registry!")
                logger.info("Chrome Version:     " + open1.value("version").value())
