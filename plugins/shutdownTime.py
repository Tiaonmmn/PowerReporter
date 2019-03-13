import os
from struct import *

from Registry import Registry
from loguru import logger
from utils import filetimeParse
import datetime


class shutdownTime:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def getLastShutdownTime(self):
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
            lastshutdown = registry.open("ControlSet00%d\\Control\\Windows" % select_current)
            logger.debug("Now listing Windows NT Last Shutdown Time using registry!")
            lastshutdownTime = filetimeParse.filetimeParse(lastshutdown.value("ShutdownTime").value())
            bias = datetime.timedelta(hours=-self.bias)
            logger.info("Last recorded shutdown time:     " + (lastshutdownTime + bias).strftime('%Y %m %d - %H:%M:%S'))
