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
