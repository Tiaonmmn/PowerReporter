__author__ = "Tiaonmmn.ZMZ"
import os
from struct import *
from . import samParse
from Registry import Registry
from loguru import logger
import subprocess


class lastLogon:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def getLastLoggedInfo(self):
        parser = samParse.samParse()
        userLoggedTime = dict()
        ''' Locate the SAM and SYSTEM file'''
        output = self.volumeInfo
        sam = 0
        SAM = 0
        system = 0
        SYSTEM = 0
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))

            if os.access("Windows/System32/config/SAM", os.F_OK | os.R_OK):
                SAM = 1
            elif os.access("Windows/System32/config/sam", os.F_OK | os.R_OK):
                sam = 1
            else:
                logger.warning("Couldn't find SAM registry file!")
                return None

        if sam == 1:
            results = parser.samparse("Windows/System32/config/sam")
        if SAM == 1:
            results = parser.samparse("Windows/System32/config/SAM")
        for user in results['users']:
            for key, value in results['users'][user].items():
                if key == 'Last Login Date':
                    userLoggedTime[user] = value
        userLoggedTime_sorted = sorted(userLoggedTime.items(), key=lambda x: x[1])

        if os.access("Windows/System32/config/software", os.F_OK | os.R_OK):
            registry = Registry.Registry("Windows/System32/config/software")
        elif os.access("Windows/System32/config/SOFTWARE", os.F_OK | os.R_OK):
            registry = Registry.Registry("Windows/System32/config/SOFTWARE")
        else:
            logger.warning("Couldn't find SOFTWARE registry file!")
            return None
        lastlogged = registry.open("Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI")
        logger.debug("Now listing Windows NT Last Logon Name using LogonUI registry!")
        logger.info("Last Logged On User Name:     " + lastlogged.value("LastLoggedOnSAMUser").value())
        logger.debug("Now listing Windows NT Last Logon Name using SAM registry!")
        logger.info("Last Logged On User Name:     " + userLoggedTime_sorted[0][0].decode())
        logger.info("Last Logged On Time:          " + userLoggedTime_sorted[0][1])
