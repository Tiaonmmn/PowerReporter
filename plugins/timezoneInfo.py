import os
from struct import *

from Registry import Registry
from loguru import logger


class timezoneInfo:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def getTimeZoneInfo(self):
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
            timezone = registry.open("ControlSet00%d\\Control\\TimeZoneInformation" % select_current)
            logger.debug("Now listing Windows NT TimeZone Information using registry!")
            logger.info("Timezone name:     " + timezone.value("TimeZoneKeyName").value())
            bias = unpack("i", pack("I", int(timezone.value("Bias").value())))[0] / 60
            dayLightBias = unpack("i", pack("I", int(timezone.value("DaylightBias").value())))[0] / 60
            activeBias = unpack("i", pack("I", int(timezone.value("ActiveTimeBias").value())))[0] / 60
            # If activeBias is positive,it really means -0X:00 delta in real world.

        if activeBias < 0:
            logger.info("Timezone real bias:     (UTC)+0%d hours" % activeBias)
        else:
            logger.info("Timezone real bias:     (UTC)-0%d hours" % activeBias)

    def getTimeZoneBias(self):
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
            timezone = registry.open("ControlSet00%d\\Control\\TimeZoneInformation" % select_current)
            logger.debug("Now listing Windows NT TimeZone Information using registry!")
            logger.info("Timezone name:     " + timezone.value("TimeZoneKeyName").value())
            bias = unpack("i", pack("I", int(timezone.value("ActiveTimeBias").value())))[0] / 60
            return bias  # TODO:Bias may be negative or positive!
