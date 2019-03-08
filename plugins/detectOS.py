import os
from loguru import logger
import subprocess
from Registry import Registry


class detectOS:
    def __init__(self, inputFile=None, mountDir=None):
        self.mountDir = mountDir
        self.inputFile = inputFile

    def detectVolumeType(self):
        output = subprocess.getoutput("mmls %s" % self.inputFile).split("Description")[-1]
        result = []
        for line in output.splitlines():
            if not line:
                continue
            try:
                values = line.split(None, 5)

                # sometimes there are only 5 elements available
                description = ''
                index, slot, start, end, length = values[0:5]
                if len(values) > 5:
                    description = values[5]
            except Exception:
                logger.critical("Error while parsing mmls output")
                continue
            if "FAT" in description and "exFAT" not in description:
                result.append("FAT %s" % index[-1])
            if "NTFS" in description:
                result.append("NTFS %s" % index[-1])
            if "Unallocated" in description:
                pass
            if "Meta" in slot:
                pass
            else:
                result.append(description + " " + index[-1])
        return result

    def detectOldWindowsVer1(self):
        output = self.detectVolumeType()
        for line in output:
            if "FAT" in line:
                for names in os.listdir(self.mountDir):
                    if line[-1] in names.split("_")[1]:
                        os.chdir(self.mountDir + names)
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

    def detectNTWindowsVer1(self):  # TODO:For now we hard-coded the registry file location.Should determine it.
        output = self.detectVolumeType()

        for line in output:
            if "FAT" in line or "NTFS" in line:
                for names in os.listdir(self.mountDir):
                    if line[-1] in names.split("_")[1]:
                        os.chdir(self.mountDir + names)
                        try:
                            try:
                                registry = Registry.Registry("Windows/System32/config/software")
                            except FileNotFoundError:
                                registry = Registry.Registry("Windows/System32/config/SOFTWARE")
                        except FileNotFoundError:
                            logger.critical("Couldn't find registry file!")
                            return None
                        osInfo = registry.open("Microsoft\\Windows NT\\CurrentVersion")
                        logger.info("Now listing Windows NT Version info using registry method!")
                        for detail in osInfo.values():
                            logger.info(
                                "{0:30}     {1:10}     {2}" % (detail.name(), detail.value_type_str(), detail.value()))
                            if "Windows 2000" in detail.value(): return "Windows 2000"
                            if "Windows XP" in detail.value(): return "Windows XP"
                            if "Windows Vista" in detail.value(): return "Windows Vista"
                            if "Windows 8" in detail.value(): return "Windows 8"
                            if "Windows 10" in detail.value(): return "Windows 10"

    def detectLinuxVer1(self):
        output = self.detectVolumeType()

        for line in output:
            if "FAT" in line or "NTFS" in line:
                pass
            else:
                for names in os.listdir(self.mountDir):
                    if line[-1] in names.split("_")[1]:
                        os.chdir(self.mountDir + names)
                        try:
                            version = open("etc/issue").read()
                        except FileNotFoundError:
                            logger.critical("Couldn't find Linux issue file!")
                            return None
                        logger.info("Found linux veriosn {0}".format(version))
                        return version.strip()


def detectOperationSystem(inputFile=None, mountDir=None):
    detector = detectOS(inputFile=inputFile, mountDir=mountDir)
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
