import os

from Registry import Registry
from loguru import logger


class detectOS:
    def __init__(self, inputFile: str, volumeInfo: str, mountDir: str):
        self.volumeInfo = volumeInfo
        self.inputFile = inputFile
        self.mountDir = mountDir

    def detectOldWindowsVer1(self) -> str:
        output = self.volumeInfo
        if "FAT" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            try:
                msdos = open("MSDOS.SYS").readlines()
            except FileNotFoundError:
                return None
            for msdosline in msdos:
                if "Winver" in msdosline:
                    version = msdosline.split("=")[-1]
                    logger.info("Found Windows version {0}".format(version))
                    if version == "4.00.0950": return "Windows 95"
                    if version == "4.00.1111": return "Windows 95 OSR2"
                    if version == "4.03.1212": return "Windows 95 OSR2.1"
                    if version == "4.03.1214": return "Windows 95 OSR2.5"
                    if version == "4.10.1998": return "Windows 98"
                    if version == "4.10.2222": return "Windows 98 SE"
                    if version == "4.90.3000":
                        return "Windows ME"
                    else:
                        return "Windows NT"
        logger.warning("Couldn't find old version Windows!")

    def detectNTWindowsVer1(self) -> str:  # TODO:For now we hard-coded the registry file location.Should determine it.
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            try:
                try:
                    registry = Registry.Registry("Windows/System32/config/software")
                except FileNotFoundError:
                    registry = Registry.Registry("Windows/System32/config/SOFTWARE")
            except FileNotFoundError:
                logger.warning("Couldn't find registry file on %s!" % ("%s/%s" % (self.mountDir, output.split(" ")[2])))
                return None
            osInfo = registry.open("Microsoft\\Windows NT\\CurrentVersion")
            logger.info("Now listing Windows NT Version info using registry method!")
            for detail in osInfo.values():
                logger.debug(
                    "{0:30}     {1:10}     {2}".format(detail.name(), detail.value_type_str(),
                                                       detail.value()))
            for detail in osInfo.values():
                if detail.name() == "ProductName":
                    logger.info("Found {0} version Windows on {1}".format(detail.value(),
                                                                          ("%s/%s" % (
                                                                              self.mountDir, output.split(" ")[2]))))
                    return detail.value()

    def detectLinuxVer1(self) -> str:
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            pass
        else:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            try:
                version = open("etc/issue").read()
            except FileNotFoundError:
                logger.warning(
                    "Couldn't find Linux issue file on %s!" % ("%s/%s" % (self.mountDir, output.split(" ")[2])))
                return None
            logger.info("Found linux veriosn {0}".format(version))
            return version.strip()


def detectOperationSystem(inputFile=None, mountDir=None, volumeInfo=None):
    detector = detectOS(inputFile=inputFile, mountDir=mountDir, volumeInfo=volumeInfo)
    result = detector.detectOldWindowsVer1()
    if result is None:
        pass
    else:
        return result
    result = detector.detectNTWindowsVer1()
    if result is None:
        pass
    else:
        return result
    result = detector.detectLinuxVer1()
    if result is None:
        pass
    else:
        return result
