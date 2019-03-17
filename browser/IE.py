from Registry import Registry
import os
import subprocess
import csv
import glob
import binascii
from loguru import logger


class IE:
    def __init__(self, volumeInfo, mountDir, tempDir):
        self.volumeInfo = volumeInfo
        self.mountDir = mountDir
        self.IEVersion = self.getIEVersion()
        self.tempDir = tempDir
        self._extractFlag = self.get_extractWebCache()
        pass

    def getIEVersion(self):
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
            if os.access("Windows/System32/config/software", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/software")
            elif os.access("Windows/System32/config/SOFTWARE", os.F_OK | os.R_OK):
                registry = Registry.Registry("Windows/System32/config/SOFTWARE")
            else:
                logger.warning("Couldn't find SOFTWARE registry file!")
                return None
            IEVersion = registry.open("Microsoft\\Internet Explorer")
            logger.debug("Now listing Windows IE Version Information using registry!")
            logger.info("Internet Explorer Version:     " + IEVersion.value("svcVersion").value())
            return IEVersion.value("svcVersion").value()

    def get_extractWebCache(self):
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10:
            output = self.volumeInfo
            if "FAT" or "NTFS" in output.split(" ")[0]:
                os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
                logger.info("Loading every user info!")  # TODO:It should be per user!
                try:
                    os.chdir("Users/")
                except FileNotFoundError:
                    logger.error("Couldn't find Users folder!")
                    return None
                for userDir in os.listdir("."):
                    try:
                        os.chdir("%s/%s" % (self.mountDir, output.split(" ")[
                            2]) + "/Users/" + userDir + "/AppData/Local/Microsoft/Windows/WebCache")
                    except (FileNotFoundError, NotADirectoryError):
                        logger.critical("Couldn't find WebCache on folder %s" %
                                        ("%s/%s" % (self.mountDir, output.split(" ")[
                                            2]) + "/Users/" + userDir + "/AppData/Local/Microsoft/Windows/WebCache"))
                        continue
                    if os.access("WebCacheV01.dat", os.R_OK | os.F_OK):
                        logger.success("WebCacheV01.dat open on folder %s OK!" % userDir)
                    else:
                        logger.critical("WebCacheV01.dat open on folder %s failed!" % userDir)
                        return None
                    logger.info("Now showing ESE DB info.")
                    logger.debug(subprocess.getoutput("esedbinfo WebCacheV01.dat"))
                    logger.info("Now extracting ESE DB info.")
                    webcachePath = os.path.realpath("WebCacheV01.dat")
                    os.chdir(self.tempDir)
                    logger.debug(
                        subprocess.getoutput("esedbexport -v %s -t WebCacheV01.dat-%s" % (webcachePath, userDir)))
                    if os.access("WebCacheV01.dat-%s.export" % userDir, os.F_OK | os.R_OK):
                        logger.success("WebCache extract OK!")
                    else:
                        logger.critical("Error extracting!")
                        return None
                return "OK"

    def getWebCacheTable(self, name):
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir)
            if len(glob.glob(r"Containers.*")) > 1:
                logger.critical("Having multiple Containers table.Please aware it.")
                for file in glob.glob(r"Containers.*"):
                    reader = csv.reader(open(file, 'r'), delimiter='\t')
                    for line in reader:  # 0:ContainerId,1:SetId,2:Flags,3:Size,4:Limit,5:LastScavengeTime,6:EntryMaxAge
                        # ,7:LastAccessTime,8:Name,9:PartitionId,10:Directory,11:SecureDirectories,12:SecureUsage,13:Group
                        if line[0] == "ContainerId":
                            continue
                        if line[8] == name:
                            return "Container_%d" % line[0]

    def getWebCacheDirectory(self, name):
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir + "/WebCacheV01.dat.export")
            if len(glob.glob(r"Containers.*")) > 1:
                logger.critical("Having multiple Containers table.Please aware it.")
                for file in glob.glob(r"Containers.*"):
                    reader = csv.reader(open(file, 'r'), delimiter='\t')
                    for line in reader:  # 0:ContainerId,1:SetId,2:Flags,3:Size,4:Limit,5:LastScavengeTime,6:EntryMaxAge
                        # ,7:LastAccessTime,8:Name,9:PartitionId,10:Directory,11:SecureDirectories,12:SecureUsage,13:Group
                        if line[0] == "ContainerId":
                            continue
                        if line[8] == name:
                            return line[10]

    def getIEContent(self):
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir)
            lists = glob.glob("WebCacheV01.dat-*.export")
            for user in lists:
                os.chdir(self.tempDir + "/" + user)
                logger.error(self.getWebCacheTable("Content"))
                filename = glob.glob(self.getWebCacheTable("Content") + ".*")[0]
                logger.debug("Now listing IE Content on user %s" % user)
                if os.access(filename, os.R_OK | os.F_OK):
                    reader = csv.reader(open(filename), delimiter="\t")
                    for line in reader:
                        # 0:EntryId,1:ContainerId,2:CacheId,3:UrlHash,4:SecureDirectory,5:FileSize,6:Type,
                        # 7:Flags,8:AccessCount,9:SyncTime,10:CreationTime,11:ExpiryTime,12:ModifiedTime,13:AccessedTime,14:PostCheckTime
                        # 15:SyncCount,16:ExemptionDelta,17:Url,18:Filename,19:FileExtension,20:RequestHeaders,21:ResponseHeaders,
                        # 22:RedirectUrl,23:Group,24ExtraData
                        if line[0] == "EntryId":
                            continue
                        logger.info("{0:20} : {1}".format("CreationTime", line[10]))
                        logger.info("{0:20} : {1}".format("Url", line[17]))
                        logger.info("{0:20} : {1}".format("Filename", line[18]))
                        logger.info("{0:20} : {1}".format("RequestHeaders", binascii.unhexlify(line[20].encode())))
                        logger.info("{0:20} : {1}".format("ResponseHeaders", binascii.unhexlify(line[21].encode())))
