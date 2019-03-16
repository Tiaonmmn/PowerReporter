from Registry import Registry
import os
import glob
from loguru import logger


class Firefox:
    def __init__(self, volumeInfo, mountDir):
        self.volumeInfo = volumeInfo
        self.mountDir = mountDir
        pass

    def getFirefoxVersion(self):
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
            timezone = registry.open("Mozilla\\Mozilla Firefox")
            logger.debug("Now listing Firefox Version Information using registry!")
            logger.info("Firefox Version:     " + timezone.value("CurrentVersion").value())
