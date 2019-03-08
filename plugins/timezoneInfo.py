import os
from Registry import Registry
from . import detectOS
from loguru import logger
from struct import *


class timezoneInfo:
    def __init__(self, inputFile=None, mountDir=None):
        self.mountDir = mountDir
        self.inputFile = inputFile

    def showtimezoneInfo(self):
        detector = detectOS.detectOS(inputFile=self.inputFile, mountDir=self.mountDir).detectVolumeType()
        for line in detector:
            if "FAT" in line or "NTFS" in line:
                for names in os.listdir(self.mountDir):
                    logger.debug("Entering dir %s" % (self.mountDir + "/" + names))
                    if line[-1] in names.split("_")[1]:
                        os.chdir(self.mountDir + "/" + names)
                        try:
                            try:
                                registry = Registry.Registry("Windows/System32/config/system")
                            except FileNotFoundError:
                                registry = Registry.Registry("Windows/System32/config/SYSTEM")
                        except FileNotFoundError:
                            logger.critical("Couldn't find registry file!")
                            continue
                        selectCurrent = registry.open("Select").value("Current").value()
                        # print(registry.open("Select").values())
                        timezone = registry.open("ControlSet00%d\\Control\\TimeZoneInformation" % selectCurrent)
                        logger.debug("Now listing Windows NT TimeZone Information using registry!")
                        logger.info("Timezone name:     " + timezone.value("TimeZoneKeyName").value())

                        logger.info("Timezone bias:     %d minutes" %
                                    (unpack("i", pack("I", int(timezone.value("ActiveTimeBias").value()))))[0])
