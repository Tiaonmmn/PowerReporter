import os
from struct import *

from Registry import Registry
from loguru import logger


class timezoneInfo:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def showTimeZoneInfo(self):
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/system", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/system")
            elif os.access("Windows/System32/config/SYSTEM", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SYSTEM")
            else:
                logger.warning("Couldn't find registry file!")
                return None
            select_current = registry.open("Select").value("Current").value()
            timezone = registry.open("ControlSet00%d\\Control\\TimeZoneInformation" % select_current)
            logger.debug("Now listing Windows NT TimeZone Information using registry!")
            logger.info("Timezone name:     " + timezone.value("TimeZoneKeyName").value())
            bias = unpack("i", pack("I", int(timezone.value("ActiveTimeBias").value())))[0] / 60
            if bias < 0:
                logger.info("Timezone bias:     (UTC)+0%d hours" % bias)
            else:
                logger.info("Timezone bias:     (UTC)-0%d hours" % bias)
