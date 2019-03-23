import datetime
import os
import subprocess
import csv
from Registry import Registry
from loguru import logger


class Explorer:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def getKeyWordAtSearchbar(self):
        output = self.volumeInfo
        result = []
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                try:
                    open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\WordWheelQuery")
                except Registry.RegistryKeyNotFoundException:
                    logger.error("Couldn't find UserAssist registry on user {0}".format(userDir))
                    continue
                logger.info("Now showing Windows Explorer searchbar info!")
                logger.info("Timestamp: " + (open1.timestamp() + bias).strftime('%Y %m %d - %H:%M:%S'))
                for item in open1.values():
                    if item.name() == 'MRUListEx':
                        continue
                    logger.info("KeyWords: %s" % (item.value().decode('utf-16-le')))
        logger.critical(result)
        return result

    def getRunMRU(self):
        output = self.volumeInfo
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU")
                networkIP = []
                logger.info("Showing Run MRU info.")
                for item in open1.values():
                    if item.name() == "MRUList":
                        continue
                    logger.info(open1.value())
                    if "\\\\" in open1.value():
                        networkIP.append(open1.value())
                logger.info("Last run time:" + (open1.timestamp() + bias).strftime("%Y %m %d - %H:%M:%S"))
        logger.critical("Found suspected network drive.%s" % networkIP)

    def getMapNetworkDriveMRU(self):
        output = self.volumeInfo
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/NTUSER.DAT".format(userDir))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    registry = Registry.Registry("{0}/ntuser.dat".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Map Network Drive MRU")
                logger.info("Showing Map Network Drive MRU info.")
                for item in open1.values():
                    if item.name() == "MRUList":
                        continue
                    logger.info(open1.value())

    # https://digital-forensics.sans.org/blog/2011/07/05/shellbags
    def getShellBag(self):
        output = self.volumeInfo
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s/" % (self.mountDir, output.split(" ")[2]))
            logger.info("Loading every user info!")  # TODO:It should be per user!
            try:
                os.chdir("Users/")
            except FileNotFoundError:
                logger.error("Couldn't find Users folder!")
                return None
            for userDir in os.listdir("."):
                if os.access("{0}/NTUSER.DAT".format(userDir), os.F_OK | os.R_OK):
                    parse_out = subprocess.getoutput("python2 {0} {1} {2} {3}".format(
                        os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                        "{0}/NTUSER.DAT".format(userDir)))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    parse_out = subprocess.getoutput("python2 {0} {1} {2} {3}".format(
                        os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                        "{0}/NTUSER.DAT".format(userDir)))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                # 0:Key Last Write Time,1:Hive,2:Modification Date,3:Accessed Date,4:Creation Date,5:Path,6:Key
                logger.info("Now showing ShellBag 1 info.")
                logger.error(parse_out)
                reader = csv.reader(parse_out, delimiter=",")
                for line in reader:
                    logger.error(line)
                    if 'No handlers could be found for logger "shellbags"' in line:
                        continue
                    if line[0] == 'Key Last Write Time':
                        continue
                    try:
                        logger.info("{0:20} : {1}".format("Modification Date",
                                                          (datetime.datetime.strptime(line[2],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Modification Date", line[2]))
                    try:
                        logger.info("{0:20} : {1}".format("Accessed Date",
                                                          (datetime.datetime.strptime(line[3],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Accessed Date", line[3]))
                    try:
                        logger.info("{0:20} : {1}".format("Creation Date",
                                                          (datetime.datetime.strptime(line[4],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Creation Date", line[4]))
                    logger.info("{0:20} : {1}".format("Path", line[5]))
                    logger.info("{0:20} : {1}".format("Key", line[6]))

                if os.access("{0}/AppData/Local/Microsoft/Windows/UsrClass.dat".format(userDir), os.F_OK | os.R_OK):
                    parse_out = subprocess.getoutput("python2 {0} {1} {2} {3}".format(
                        os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                        "{0}/AppData/Local/Microsoft/Windows/UsrClass.dat".format(userDir)))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                # 0:Key Last Write Time,1:Hive,2:Modification Date,3:Accessed Date,4:Creation Date,5:Path,6:Key
                logger.info("Now showing ShellBag 2 info.")
                reader = csv.reader(parse_out, delimiter=",")
                for line in reader:
                    if 'No handlers could be found for logger "shellbags"' in line:
                        continue
                    if line[0] == 'Key Last Write Time':
                        continue
                    try:
                        logger.info("{0:20} : {1}".format("Key Last Write Time",
                                                          (datetime.datetime.strptime(line[0],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Key Last Write Time", line[0]))

                    logger.info("{0:20} : {1}".format("Hive", line[1]))
                    try:
                        logger.info("{0:20} : {1}".format("Modification Date",
                                                          (datetime.datetime.strptime(line[2],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Modification Date", line[2]))
                    try:
                        logger.info("{0:20} : {1}".format("Accessed Date",
                                                          (datetime.datetime.strptime(line[3],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Accessed Date", line[3]))
                    try:
                        logger.info("{0:20} : {1}".format("Creation Date",
                                                          (datetime.datetime.strptime(line[4],
                                                                                      "%m/%d/%Y %H:%M:%S") + bias).strftime(
                                                              "%Y %m %d - %H:%M:%S")))
                    except ValueError:
                        logger.info("{0:20} : {1}".format("Creation Date", line[4]))
                    logger.info("{0:20} : {1}".format("Path", line[5]))
                    logger.info("{0:20} : {1}".format("Key", line[6]))
