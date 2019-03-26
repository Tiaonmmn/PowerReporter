import os

from Registry import Registry
from loguru import logger


class printers:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def showPrintersInfo(self):
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
            printers = registry.open("Microsoft\\Windows NT\\CurrentVersion\\Print\\Printers")
            logger.debug(
                "Now listing Windows NT Printers Information using Microsoft\\Windows NT\\CurrentVersion\\Print\\Printers registry key!")
            for item in printers.subkeys():
                logger.info("Printer Name : " + item.name())
                for printer_detail in item.values():
                    logger.info("{0:25} : {1}".format(printer_detail.name(), printer_detail.value()))

    def getDefaultPrinterByUserName(self, userName) -> str:
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
                if userName == userDir:
                    if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                    elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                    else:
                        logger.warning("Couldn't find user registry on %s" % userDir)
                        continue
                    try:
                        open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Windows")
                    except Registry.RegistryKeyNotFoundException:
                        logger.error("Couldn't open registry on user {0}".format(userDir))
                        continue
                    try:
                        legacyMode = open1.value("LegacyDefaultPrinterMode").value()
                        if legacyMode == 0:
                            logger.info("User doesn't enable LegacyDefaultPrinterMode! The default printer is normal!")
                        if legacyMode == 1:
                            logger.info("User enables LegacyDefaultPrinterMode! The default printer is the last printer!")
                    except Registry.RegistryKeyNotFoundException:
                        logger.info("OS is not Windows 10,no LegacyDefaultPrinterMode exists!")
                        pass
                    device = open1.value("Device").value().split(",")[0]
                    logger.info("Now showing user {0} default printer!".format(userDir))
                    logger.debug("Default printer : {0}".format(device))
        return device
