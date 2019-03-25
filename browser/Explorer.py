import datetime
import os
import struct
import glob
import subprocess
from Registry import Registry
from plugins import customShellFolder
from loguru import logger
from thirdParty import jumplist_tool


class Explorer:
    def __init__(self, mountDir: str, volumeInfo: str, bias, outputDir):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias
        self.outputDir = outputDir

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
                try:
                    open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU")
                except Registry.RegistryKeyNotFoundException:
                    logger.critical("Couldn't find RunMRU key on %s" % userDir)
                    continue
                networkIP = []
                logger.info("Showing Run MRU info.")
                for item in open1.values():
                    if item.name() == "MRUList":
                        continue
                    logger.info(item.value())
                    if "\\\\" in item.value():
                        networkIP.append(item.value())
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
                try:
                    open1 = registry.open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Map Network Drive MRU")
                except Registry.RegistryKeyNotFoundException:
                    logger.critical("Couldn't find Map Network Drive MRU key on %s" % userDir)
                    continue
                logger.info("Showing Map Network Drive MRU info.")
                for item in open1.values():
                    if item.name() == "MRUList":
                        continue
                    logger.info(item.value())

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
                    parse_out = subprocess.getoutput("python2 {0} {1} {2} '{3}'".format(
                        os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                        "{0}/NTUSER.DAT".format(userDir)))
                elif os.access("{0}/ntuser.dat".format(userDir), os.F_OK | os.R_OK):
                    parse_out = subprocess.getoutput("python2 {0} {1} {2} '{3}'".format(
                        os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                        "{0}/NTUSER.DAT".format(userDir)))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                # 0:Key Last Write Time,1:Hive,2:Modification Date,3:Accessed Date,4:Creation Date,5:Path,6:Key
                logger.info("Now showing ShellBag 1 info.")
                logger.error(parse_out)
                reader = parse_out.splitlines()
                print(["python2", os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o", "csv",
                       "{0}/NTUSER.DAT".format(userDir)])
                # "python2 {0} {1} {2} {3}".format(
                #         os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                #         "{0}/NTUSER.DAT".format(userDir)))))
                for line in reader:
                    logger.error(line)
                    line = line.split(",")
                    # if 'No handlers could be found for logger "shellbags"' in line:
                    #     continue
                    # if line[0] == 'Key Last Write Time':
                    #     continue
                    if line[0] == 'K' or line[0] == 'N':
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
                # os.chdir(oldcwd)
                if os.access("{0}/AppData/Local/Microsoft/Windows/UsrClass.dat".format(userDir), os.F_OK | os.R_OK):
                    parse_out = subprocess.getoutput("python2 {0} {1} {2} '{3}'".format(
                        os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/shellbags.py", "-v", "-o csv",
                        "{0}/AppData/Local/Microsoft/Windows/UsrClass.dat".format(userDir)))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                # 0:Key Last Write Time,1:Hive,2:Modification Date,3:Accessed Date,4:Creation Date,5:Path,6:Key
            logger.info("Now showing ShellBag 2 info.")
            reader = parse_out.splitlines()
            for line in reader:
                line = line.split(",")
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

    def getJumpList(self):
        # https://www.forensicswiki.org/wiki/Jump_Lists
        jumpList = jumplist_tool.jumpList()
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
                if os.access("{0}/AppData/Roaming/Microsoft/Windows/Recent/AutomaticDestinations".format(userDir),
                             os.F_OK | os.R_OK):
                    fileList = os.listdir("{0}/AppData/Roaming/Microsoft/Windows/Recent/AutomaticDestinations/".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                fileList = ["{0}/AppData/Roaming/Microsoft/Windows/Recent/AutomaticDestinations/".format(userDir) + a for a in
                            fileList]
                for file in fileList:
                    logger.info(file)
                    try:
                        jumpList.read_auto(file)
                    except (AssertionError, struct.error):
                        logger.critical("Not valid autoJump file!")
                        continue
                if os.access("{0}/AppData/Roaming/Microsoft/Windows/Recent/CustomDestinations".format(userDir),
                             os.F_OK | os.R_OK):
                    fileList = os.listdir("{0}/AppData/Roaming/Microsoft/Windows/Recent/CustomDestinations/".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                fileList = ["{0}/AppData/Roaming/Microsoft/Windows/Recent/CustomDestinations/".format(userDir) + a for a in
                            fileList]
                for file in fileList:
                    try:
                        jumpList.read_custom(file)
                    except AssertionError:
                        logger.critical("Not valid customJump file!")
                        continue

    def getRecentLNKInfo(self):
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
                if os.access("{0}/AppData/Roaming/Microsoft/Windows/Recent/".format(userDir),
                             os.F_OK | os.R_OK):
                    fileList = os.listdir("{0}/AppData/Roaming/Microsoft/Windows/Recent/".format(userDir))
                else:
                    logger.warning("Couldn't find user registry on %s" % userDir)
                    continue
                fileList = ["{0}/AppData/Roaming/Microsoft/Windows/Recent/".format(userDir) + a for a in
                            fileList]
                for file in fileList:
                    if os.path.isdir(file):
                        continue
                    logger.info("Now showing Recent lnk file %s info!" % file)
                    logger.debug(subprocess.getoutput(
                        "python2 {0} '{1}'".format(os.path.dirname(os.path.realpath(__file__)) + "/../thirdParty/lnkparse.py",
                                                   file)))

    def showDesktopFiles(self):
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
                try:
                    desktopPath = customShellFolder.customShellFolder(mountDir=self.mountDir,
                                                                      volumeInfo=self.volumeInfo).getCustomShellFolderByUserName(
                        userDir)[0]['Desktop']
                except Exception as e:
                    logger.critical(e)
                    continue
                desktopPath = desktopPath.replace("\\", "/").replace("%USERPROFILE%", os.path.realpath(".") + "/" + userDir)
                logger.error(desktopPath)
                if os.access(desktopPath, os.F_OK | os.R_OK):
                    logger.debug(subprocess.getoutput("ls -laRh '{0}'".format(desktopPath)))
                else:
                    logger.warning("Couldn't find user desktopPath %s." % desktopPath)
                    continue

    def _getThumbCacheFilesByUser(self, userName):
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
                if userName != userDir:
                    continue
                if os.access("{0}/AppData/Local/Microsoft/Windows/Explorer/".format(userDir), os.F_OK | os.R_OK):
                    pass
                else:
                    logger.critical("Couldn't find Explorer path!")
                    continue
                fileList = glob.glob("{0}/AppData/Local/Microsoft/Windows/Explorer/thumbcache*.db".format(userDir))
                if fileList is []:
                    logger.critical("Thumbcache not found on user %s!" % userDir)
                    continue
                logger.critical(fileList)
                return fileList

    def extractThumbCacheFiles(self):
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
                thumbcacheFileList = self._getThumbCacheFilesByUser(userDir)
                if thumbcacheFileList is None: continue
                for item in thumbcacheFileList:
                    dirName = self.outputDir + "/{0}-{1}".format(item.split("/")[-1], userDir)
                    try:
                        os.mkdir(dirName)
                    except FileExistsError:
                        subprocess.call(['rm', '-rfv', dirName])
                        os.mkdir(dirName)
                    logger.info("Now extracting user %s thumbcache file %s" % (userDir, item))
                    logger.debug(subprocess.getoutput("{0} {1} {2} {3} {4} {5}".format("wine", os.path.realpath(
                        __file__ + "/../../thirdParty/ThumbCacheExtractor.exe"), "-o", dirName, "-w", os.getcwd() + "/" + item)))
        logger.warning("Thumbcache is extracted in %s.Please see it manually." % self.outputDir)
