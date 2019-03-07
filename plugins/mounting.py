import subprocess

from loguru import logger


class mounting:
    def __init__(self, inputFile, mountDir):
        self.inputFile = inputFile
        self.mountDir = mountDir
        pass

    def showVolumeInfo(self):
        logger.info("Now let's see the volume info of this image!")
        logger.debug(subprocess.getoutput("mmls -v %s" % self.inputFile))

    def realMount(self):
        logger.debug(subprocess.getoutput(
            ["./imagemounter/imount.py", "--no-interaction", "-v", "-v", "-v", "--mountdir", "%s" % self.mountDir,
             "%s" % self.inputFile]))

    def umount(self):
        logger.debug(subprocess.getoutput(
            ["./imagemounter/imount.py", "--no-interaction", "-v", "-v", "-v", "-u", "--mountdir",
             "%s" % self.mountDir]))


def mountImage(inputFile=None, mountDir=None):
    mount = mounting(inputFile, mountDir)
    mount.showVolumeInfo()
    mount.realMount()


def unmountImage(mountDir):
    mount = mounting(None, mountDir)
    mount.umount()
