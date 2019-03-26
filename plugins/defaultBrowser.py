import os

from Registry import Registry
from loguru import logger


class defaultBrowser:
    def __init__(self, mountDir: str, volumeInfo: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo

    def getDefaultBrowserByUserName(self, userName):
        output = self.volumeInfo

        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if userName == userDir:
                    if os.access("{0}/AppData/Local/Microsoft/Windows/UsrClass.dat".format(userDir), os.F_OK | os.R_OK):
                        registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                    else:
                        logger.warning("Couldn't find user registry on %s" % userDir)
                        continue
                    try:
                        open1 = registry.open("http\\shell\\open\\command")
                    except Registry.RegistryKeyNotFoundException:
                        logger.error("Couldn't find UsrClass http registry on user {0}".format(userDir))
                        continue
                    logger.info("Now showing %s default http open info!" % userDir)
                    logger.debug("Default HTTP open handler : {0}".format(open1.value("(default)").value()))
                    try:
                        open2 = registry.open("https\\shell\\open\\command")
                    except Registry.RegistryKeyNotFoundException:
                        logger.error("Couldn't find UsrClass https registry on user {0}".format(userDir))
                        continue
                    logger.info("Now showing %s default http open info!" % userDir)
                    logger.debug("Default HTTPS open handler : {0}".format(open2.value("(default)").value()))
                    try:
                        open3 = registry.open(".html")
                    except Registry.RegistryKeyNotFoundException:
                        logger.error("Couldn't find UsrClass http registry on user {0}".format(userDir))
                        continue
                    html_value = open3.value("(default)").value()
                    try:
                        open4 = registry.open(html_value)
                    except Registry.RegistryKeyNotFoundException:
                        logger.error(".html association on user {0} may be broken!".format(userDir))
                        continue
                    logger.info("Now showing %s default .html open info!" % userDir)
                    logger.debug("Default .html open handler : {0}".format(
                        open4.subkey("shell").subkey("open").subkey("command").value("(default)").value()))
