import os
from loguru import logger
import subprocess


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

        def detectOldWindows(self):
            output = self.detectVolumeType()
            for line in output:
                if "FAT" in line:
                    for names in os.listdir(self.mountDir):
                        if line[-1] in names.split("_")[1]:
                            os.chdir(self.mountDir + names)
                            try:
                                msdos = open("MSDOS.SYS").readlines()
                            except FileNotFoundError:
                                continue
                            for msdosline in msdos:
                                if "Winver" in msdosline:
                                    version = msdosline.split("=")[-1]
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
