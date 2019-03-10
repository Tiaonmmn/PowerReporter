import os
import datetime
from Registry import Registry
from loguru import logger


class osInstalledTime:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def getOSInstalledTime(self):
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
            installedTime = datetime.datetime.fromtimestamp(
                registry.open("Microsoft\\Windows NT\\CurrentVersion").value("InstallDate").value())
            logger.debug(
                "Now listing Windows NT Install Time using HKLM\\Microsoft\\Windows NT\\CurrentVersion\\InstallDate registry key!")
            logger.info("{0:25} : {1}".format("System installed date", installedTime.strftime('%d %B %Y - %H:%M:%S')))
