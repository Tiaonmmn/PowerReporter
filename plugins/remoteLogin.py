import os

from Registry import Registry
from loguru import logger


class remoteLogin:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def getRemoteDesktopEnabled(self):
        output = self.volumeInfo
        result = dict()
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
            open1 = registry.open("ControlSet00%d\\Control\\Terminal Server" % (select_current))
            opened = open1.value("fDenyTSConnections").value()
            if opened == 1:
                logger.info("Remote Desktop Service is not enabled!")
                result['Enabled'] = False
            else:
                logger.info("Remote Desktop Service is enabled!")
                result['Enabled'] = True
            port = open1.subkey("WinStations").subkey("RDP-Tcp").value("PortNumber").value()
            logger.info("Remote Desktop Service port number is {0}.".format(port))
            result['PortNumber'] = port
        return result
