import os
from struct import *

from Registry import Registry
from loguru import logger


class lastShutdown:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def showLastShutdownTime(self):
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/software", os.R_OK | os.F_OK):
                registry = Registry.Registry("Windows/System32/config/software")
            elif os.access("Windows/System32/config/SOFTWARE", os.R_OK | os.F_OK):
                registry = Registry.Registry("Windows/System32/config/SOFTWARE")
            else:
                logger.warning("Couldn't find registry file!")
                return None
            lastlogged = registry.open("Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI")
            logger.debug("Now listing Windows NT Last Logon Information using registry!")
            logger.info("Last Logged On User Name:     " + lastlogged.value("LastLoggedOnSAMUser").value())
