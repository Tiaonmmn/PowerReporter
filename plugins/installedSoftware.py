__author__ = "Tiaonmmn.ZMZ"
import os
from Registry import Registry
from loguru import logger


class installedSoftware:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def getInstalledSoftwareInfoWin64(self):
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
        installed = registry.open("Microsoft\\Windows\\CurrentVersion\\Uninstall")
        logger.debug("Showing Installed Software Information Part 1-Win64 Applications.")
        for software in installed.subkeys():
            try:
                displayName = software.value("DisplayName").value()
            except:
                displayName = None
            for detail in software.values():
                if displayName is None:
                    logger.info("{0:25} is system component.".format(software.name()))
                else:
                    logger.info("{0:25} : {1}".format(detail.name(), detail.value()))

    def getInstalledSoftwareInfoWin32(self):
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
        installed = registry.open("Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall")
        logger.debug("Showing Installed Software Information Part 2-Win32 Applications.")
        for software in installed.subkeys():
            try:
                displayName = software.value("DisplayName").value()
            except:
                displayName = None
            for detail in software.values():
                if displayName is None:
                    logger.info("{0:25} is system component.".format(software.name()))
                else:
                    logger.info("{0:25} : {1}".format(detail.name(), detail.value()))
