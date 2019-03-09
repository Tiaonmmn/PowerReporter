import os
import subprocess

from loguru import logger


class mounting:
    def __init__(self, inputFile=None, mountDir=None):
        self.inputFile = inputFile
        self.mountDir = mountDir
        pass

    def showVolumeInfo(self):
        logger.debug("Now let's see the volume info of this image!")
        # logger.debug(subprocess.call("mmls -v %s" % self.inputFile))
        logger.debug(subprocess.call(["mmls", "-v", "%s" % self.inputFile]))

    def realMount(self):
        logger.debug(subprocess.call(
            [os.path.dirname(os.path.realpath(__file__)) + "/../" + "./imagemounter/imount.py",
             "--no-interaction",
             "-v", "-v", "-v", "--mountdir", "%s" % self.mountDir,
             "%s" % self.inputFile]))
        # logger.debug(subprocess.call(
        #     "./imagemounter/imount.py --no-interaction -v -v -v --mountdir %s %s " % (self.mountDir, self.inputFile)))

    def umount(self):
        logger.debug(subprocess.call(
            [os.path.dirname(os.path.realpath(__file__)) + "/../" + "./imagemounter/imount.py", "--no-interaction",
             "-v",
             "-v", "-v", "-u", "--mountdir",
             "%s" % self.mountDir]))
        # logger.debug(subprocess.call(
        #     "./imagemounter/imount.py --no-interaction -v -v -v -u --mountdir %s" % self.mountDir))

    def detectVolumeType(self):
        output = subprocess.getoutput("mmls %s" % self.inputFile).split("Description")[-1]
        result = []
        for line in output.splitlines():
            if not line:
                continue
            try:
                values = line.split()
                # sometimes there are only 5 elements available
                description = ''
                index, slot, start, end, length = values[0:5]
                if len(values) > 5:
                    description = values[5]
            except Exception:
                logger.critical("Error while parsing mmls output")
                continue
            if "FAT" in description and "exFAT" not in description:
                result.append("FAT %s" % index[-2])
            if "NTFS" in description:
                result.append("NTFS %s" % index[-2])
            if "Unallocated" in description:
                pass
            if "Meta" in slot:
                pass
            else:
                result.append(description + " " + index[-2])
        result = list(set(result))
        return result

    def getVolumeDirectory(self):
        results = self.detectVolumeType()
        volumeInfo = []
        directoryNames = os.listdir(self.mountDir)
        for name in directoryNames:
            for result in results:
                if result[-1] == name.split("_")[1]:
                    volumeInfo.append(
                        "%s %s %s" % (result.split(" ")[0], result.split(" ")[1],
                                      name))  # return a string:[volume fs] [volume index] [volume directory]
        return volumeInfo


def mountImage(inputFile=None, mountDir="/tmp/"):
    mount = mounting(inputFile, mountDir)
    mount.showVolumeInfo()
    mount.realMount()
    mount.getVolumeDirectory()
    return mount


def unmountImage(mountDir):
    mount = mounting(None, mountDir)
    mount.umount()
