import os
from Registry import Registry
from loguru import logger


class applicationExecutionLog:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def getNetworkDeviceInfo(self):
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
        tcpipInterfaces = registry.open("ControlSet00%d\\Services\\Tcpip\\Parameters\\Interfaces" % (select_current))
        for interface in tcpipInterfaces.subkeys():
            logger.debug("Showing information about device %s" % (interface.name()))
            for detail in interface.values():
                logger.info("{0:25} : {1}".format(detail.name(), detail.value()))
