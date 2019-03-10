import os

from Registry import Registry
from loguru import logger


class computerName:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def showComputerName(self):
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/system", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/system")
            elif os.access("Windows/System32/config/SYSTEM", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SYSTEM")
            else:
                logger.warning("Couldn't find SYSTEM registry file!")
                return None
            select_current = registry.open("Select").value("Current").value()
            computerName1 = registry.open("ControlSet00%d\\Control\\ComputerName" % select_current)
            logger.debug(
                "Now listing Windows NT ComputerName Information using ControlSet00%d\\Control\\ComputerName registry key!" % select_current)
            logger.info(
                "Computer Name version 1:     " + computerName1.subkey("ComputerName").value("ComputerName").value())
            logger.debug(
                "Now listing Windows NT ComputerName Information using ControlSet00%d\\services\\Tcpip\\Parameters\\Hostname registry key!" % select_current)
            computerName2 = registry.open("ControlSet00%d\\services\\Tcpip" % select_current)
            logger.info("Computer Name version 2:     " + computerName2.subkey("Parameters").value("Hostname").value())
