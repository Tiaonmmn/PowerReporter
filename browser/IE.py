from Registry import Registry
import os
import subprocess
import csv
import glob
import binascii
import datetime
from loguru import logger
import urllib
from . import oldIE

class IE:

    def __init__(self, volumeInfo, mountDir, tempDir):
        self._userList = []
        self.volumeInfo = volumeInfo
        self.mountDir = mountDir
        self.IEVersion = self.getIEVersion()
        self.tempDir = tempDir
        self._extractFlag = self.get_extractWebCache()
        self._ieCookies = self.getIECookies()
        self._ieHistory = self.getIEHistory()
        self._ieContent = self.getIEContent()
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
            if "svcVersion" in IEVersion.values():
                logger.info("Internet Explorer Version:     " + IEVersion.value("svcVersion").value())
                return IEVersion.value("svcVersion").value()
            else:
                logger.info("Internet Explorer Version:     " + IEVersion.value("Version").value())
                return IEVersion.value("Version").value()

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
                        self._userList.append(userDir)
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

    def getWebCacheDirectory(self, tableName, userName, PartitionId):  # PartitionId is optional
        result = []
        if self.IEVersion is None:
            logger.error("Coudln't parse IE Version!")
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir + "/WebCacheV01.dat-%s.export" % userName)
            if len(glob.glob(r"Containers.*")) > 1:
                logger.critical("Having multiple Containers table.Please aware it.")
            for file in glob.glob(r"Containers.*"):
                reader = csv.reader(open(file, 'r'), delimiter='\t')
                for line in reader:  # 0:ContainerId,1:SetId,2:Flags,3:Size,4:Limit,5:LastScavengeTime,6:EntryMaxAge
                    # ,7:LastAccessTime,8:Name,9:PartitionId,10:Directory,11:SecureDirectories,12:SecureUsage,13:Group
                    if line[0] == "ContainerId":
                        continue
                    if PartitionId:
                        if PartitionId == line[9] and tableName == line[8]:
                            result.append("Container_%s" % line[10])
                    else:
                        if tableName == line[8]:
                            result.append("Container_%s" % line[10])
        return result

    def parseWebCacheDirectory(self, tableName, userName, PartitionId):
        source = self.getWebCacheDirectory(tableName, userName, PartitionId)
        output = self.volumeInfo
        result = []
        for item in source:
            parts = item.replace("\\", "//").split("//")
            parts[0] = "%s/%s" % (self.mountDir, output.split(" ")[2])
            result.append("/".join(str(i) for i in parts))
        return result

    def getWebCacheTable(self, tableName, userName, PartitionId):  # PartitionId is optional
        result = []
        if self.IEVersion is None:
            logger.error("Coudln't parse IE Version!")
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir + "/WebCacheV01.dat-%s.export" % userName)
            if len(glob.glob(r"Containers.*")) > 1:
                logger.critical("Having multiple Containers table.Please aware it.")
            for file in glob.glob(r"Containers.*"):
                reader = csv.reader(open(file, 'r'), delimiter='\t')
                for line in reader:  # 0:ContainerId,1:SetId,2:Flags,3:Size,4:Limit,5:LastScavengeTime,6:EntryMaxAge
                    # ,7:LastAccessTime,8:Name,9:PartitionId,10:Directory,11:SecureDirectories,12:SecureUsage,13:Group
                    if line[0] == "ContainerId":
                        continue
                    if PartitionId:
                        if PartitionId == line[9] and tableName == line[8]:
                            result.append("Container_%s" % line[0])
                    else:
                        if tableName == line[8]:
                            result.append("Container_%s" % line[0])
        return result

    def getIEContent(self):
        ieContent = []
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir)
            for user in self._userList:
                os.chdir(self.tempDir + "/WebCacheV01.dat-%s.export" % user)
                logger.error("parsing %s WebCache" % user)
                for item in self.getWebCacheTable(tableName="Content", userName=user, PartitionId=None):
                    filename = glob.glob(item + ".*")[0]
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
                            tempContent = dict()
                            logger.info(
                                "{0:20} : {1}".format("CreationTime", datetime.datetime.strptime(line[10].split(".")[0],
                                                                                                 "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            logger.info("{0:20} : {1}".format("Filename", line[18]))
                            logger.info("{0:20} : {1}".format("RequestHeaders", binascii.unhexlify(line[20].encode())))
                            logger.info("{0:20} : {1}".format("ResponseHeaders", binascii.unhexlify(line[21].encode())))
                            tempContent['CreationTime'] = datetime.datetime.strptime(line[10].split(".")[0],
                                                                                     "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempContent['Url'] = line[17]
                            tempContent['Filename'] = line[18]
                            tempContent['RequestHeaders'] = binascii.unhexlify(line[20].encode())
                            tempContent['ResponseHeaders'] = binascii.unhexlify(line[21].encode())
                            ieContent.append(tempContent)
            return ieContent
        else:
            oldIE

    def getIEHistory(self):
        ieHistory = []
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir)
            for user in self._userList:
                os.chdir(self.tempDir + "/WebCacheV01.dat-%s.export" % user)
                logger.error("parsing %s WebCache" % user)

                for item in self.getWebCacheTable(tableName="History", userName=user, PartitionId='M'):
                    filename = glob.glob(item + ".*")[0]
                    logger.debug("Now listing IE History 1 on user %s" % user)
                    if os.access(filename, os.R_OK | os.F_OK):
                        reader = csv.reader(open(filename), delimiter="\t")
                        for line in reader:
                            # 0: EntryId, 1: ContainerId, 2: CacheId, 3: UrlHash, 4: SecureDirectory, 5: FileSize, 6: Type,
                            # 7: Flags, 8: AccessCount, 9: SyncTime, 10: CreationTime, 11: ExpiryTime, 12: ModifiedTime,
                            # 13: AccessedTime, 14: PostCheckTime, 15: SyncCount, 16: ExemptionDelta, 17: Url, 18: Filename,
                            # 19: FileExtension, 20: RequestHeaders, 21: ResponseHeaders, 22: RedirectUrl, 23: Group, 24: ExtraData                            if line[0] == "EntryId":
                            if line[0] == "EntryId":
                                continue
                            tempHistory = dict()
                            logger.info(
                                "{0:20} : {1}".format("CreationTime", datetime.datetime.strptime(line[10].split(".")[0],
                                                                                                 "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info(
                                "{0:20} : {1}".format("AccessTime", datetime.datetime.strptime(line[13].split(".")[0],
                                                                                               "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            tempHistory['CreationTime'] = datetime.datetime.strptime(line[10].split(".")[0],
                                                                                     "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempHistory['AccessTime'] = datetime.datetime.strptime(line[13].split(".")[0],
                                                                                   "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempHistory['Url'] = line[17]
                            ieHistory.append(tempHistory)

                for item in self.getWebCacheTable(tableName="History", userName=user, PartitionId='L'):
                    filename = glob.glob(item + ".*")[0]
                    logger.debug("Now listing IE History 2 on user %s" % user)
                    if os.access(filename, os.R_OK | os.F_OK):
                        reader = csv.reader(open(filename), delimiter="\t")
                        for line in reader:
                            # 0: EntryId, 1: ContainerId, 2: CacheId, 3: UrlHash, 4: SecureDirectory, 5: FileSize, 6: Type,
                            # 7: Flags, 8: AccessCount, 9: SyncTime, 10: CreationTime, 11: ExpiryTime, 12: ModifiedTime,
                            # 13: AccessedTime, 14: PostCheckTime, 15: SyncCount, 16: ExemptionDelta, 17: Url, 18: Filename,
                            # 19: FileExtension, 20: RequestHeaders, 21: ResponseHeaders, 22: RedirectUrl, 23: Group, 24: ExtraData                            if line[0] == "EntryId":
                            if line[0] == "EntryId":
                                continue
                            tempHistory = dict()
                            logger.info(
                                "{0:20} : {1}".format("CreationTime", datetime.datetime.strptime(line[10].split(".")[0],
                                                                                                 "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info(
                                "{0:20} : {1}".format("AccessTime", datetime.datetime.strptime(line[13].split(".")[0],
                                                                                               "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            tempHistory['CreationTime'] = datetime.datetime.strptime(line[10].split(".")[0],
                                                                                     "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempHistory['AccessTime'] = datetime.datetime.strptime(line[13].split(".")[0],
                                                                                   "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempHistory['Url'] = line[17]
                            ieHistory.append(tempHistory)
        return ieHistory

    def getIECookies(self):
        ieCookies = []
        if self.IEVersion is None:
            return None
        if int(self.IEVersion.split(".")[0]) >= 10 and self._extractFlag == "OK":
            os.chdir(self.tempDir)
            for user in self._userList:
                os.chdir(self.tempDir + "/WebCacheV01.dat-%s.export" % user)
                logger.error("parsing %s WebCache" % user)
                for item in self.getWebCacheTable(tableName="Cookies", userName=user, PartitionId='M'):
                    filename = glob.glob(item + ".*")[0]
                    logger.debug("Now listing IE Cookies 1 on user %s" % user)
                    if os.access(filename, os.R_OK | os.F_OK):
                        reader = csv.reader(open(filename), delimiter="\t")
                        for line in reader:
                            # 0: EntryId, 1: ContainerId, 2: CacheId, 3: UrlHash, 4: SecureDirectory, 5: FileSize, 6: Type,
                            # 7: Flags, 8: AccessCount, 9: SyncTime, 10: CreationTime, 11: ExpiryTime, 12: ModifiedTime,
                            # 13: AccessedTime, 14: PostCheckTime, 15: SyncCount, 16: ExemptionDelta, 17: Url, 18: Filename,
                            # 19: FileExtension, 20: RequestHeaders, 21: ResponseHeaders, 22: RedirectUrl, 23: Group, 24: ExtraData                            if line[0] == "EntryId":
                            if line[0] == "EntryId":
                                continue
                            tempCookies = dict()
                            logger.info(
                                "{0:20} : {1}".format("CreationTime", datetime.datetime.strptime(line[10].split(".")[0],
                                                                                                 "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info(
                                "{0:20} : {1}".format("ExpiryTime", datetime.datetime.strptime(line[11].split(".")[0],
                                                                                               "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info(
                                "{0:20} : {1}".format("AccessTime", datetime.datetime.strptime(line[13].split(".")[0],
                                                                                               "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            logger.info("{0:20} : {1}".format("Filename", line[18]))
                            try:
                                logger.info("{0:20} : {1}".format("Cookies contents", open(
                                    self.parseWebCacheDirectory(tableName="Cookies", userName=user,
                                                                PartitionId='M')[0] + "/" + line[18]).read()))
                            except FileNotFoundError:
                                logger.critical("Couldn't find cookies file %s.Please aware it." %
                                                self.parseWebCacheDirectory(tableName="Cookies", userName=user,
                                                                            PartitionId='L')[0] + "/" + line[18])

                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            tempCookies['CreationTime'] = datetime.datetime.strptime(line[10].split(".")[0],
                                                                                     "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempCookies['ExpiryTime'] = datetime.datetime.strptime(line[11].split(".")[0],
                                                                                   "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempCookies['AccessTime'] = datetime.datetime.strptime(line[13].split(".")[0],
                                                                                   "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempCookies['Url'] = line[17]
                            tempCookies['Filename'] = line[18]
                            ieCookies.append(tempCookies)

                for item in self.getWebCacheTable(tableName="Cookies", userName=user, PartitionId='L'):
                    filename = glob.glob(item + ".*")[0]
                    logger.debug("Now listing IE History 2 on user %s" % user)
                    if os.access(filename, os.R_OK | os.F_OK):
                        logger.error(filename)
                        reader = csv.reader(open(filename), delimiter="\t")
                        for line in reader:
                            # 0: EntryId, 1: ContainerId, 2: CacheId, 3: UrlHash, 4: SecureDirectory, 5: FileSize, 6: Type,
                            # 7: Flags, 8: AccessCount, 9: SyncTime, 10: CreationTime, 11: ExpiryTime, 12: ModifiedTime,
                            # 13: AccessedTime, 14: PostCheckTime, 15: SyncCount, 16: ExemptionDelta, 17: Url, 18: Filename,
                            # 19: FileExtension, 20: RequestHeaders, 21: ResponseHeaders, 22: RedirectUrl, 23: Group, 24: ExtraData                            if line[0] == "EntryId":
                            if line[0] == "EntryId":
                                continue
                            tempCookies = dict()
                            logger.info(
                                "{0:20} : {1}".format("CreationTime", datetime.datetime.strptime(line[10].split(".")[0],
                                                                                                 "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info(
                                "{0:20} : {1}".format("ExpiryTime", datetime.datetime.strptime(line[11].split(".")[0],
                                                                                               "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info(
                                "{0:20} : {1}".format("AccessTime", datetime.datetime.strptime(line[13].split(".")[0],
                                                                                               "%b %d, %Y %H:%M:%S").strftime(
                                    "%Y %m %d - %H:%M:%S")))
                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            logger.info("{0:20} : {1}".format("Filename", line[18]))
                            try:
                                logger.info("{0:20} : {1}".format("Cookies contents", open(
                                    self.parseWebCacheDirectory(tableName="Cookies", userName=user,
                                                                PartitionId='L')[0] + "/" + line[18]).read()))
                            except FileNotFoundError:
                                logger.critical("Couldn't find cookies file %s.Please aware it." %
                                                self.parseWebCacheDirectory(tableName="Cookies", userName=user,
                                                                            PartitionId='L')[0] + "/" + line[18])

                            logger.info("{0:20} : {1}".format("Url", line[17]))
                            tempCookies['CreationTime'] = datetime.datetime.strptime(line[10].split(".")[0],
                                                                                     "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempCookies['ExpiryTime'] = datetime.datetime.strptime(line[11].split(".")[0],
                                                                                   "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempCookies['AccessTime'] = datetime.datetime.strptime(line[13].split(".")[0],
                                                                                   "%b %d, %Y %H:%M:%S").strftime(
                                "%Y %m %d - %H:%M:%S")
                            tempCookies['Url'] = line[17]
                            tempCookies['Filename'] = line[18]
                            ieCookies.append(tempCookies)
        return ieCookies

    def getIEKeyWords(self):
        time_url = []
        keyWordList = []
        if self._ieContent is None or self._ieCookies is None or self._ieHistory is None:
            logger.critical("Couldn't find Internet Explorer elements!")
            return None
        for historyLine in self._ieHistory:
            tempHistory = dict()
            tempHistory['CreationTime'] = historyLine['CreationTime']
            tempHistory['Url'] = historyLine['Url']
            tempHistory['Source'] = "History"
            time_url.append(tempHistory)
        for cookiesLine in self._ieCookies:
            tempCookies = dict()
            tempCookies['CreationTime'] = cookiesLine['CreationTime']
            tempCookies['Url'] = cookiesLine['Url']
            tempCookies['Source'] = "Cookies"
            time_url.append(tempCookies)
        for contentLine in self._ieContent:
            tempContent = dict()
            tempContent['CreationTime'] = contentLine['CreationTime']
            tempContent['Url'] = contentLine['Url']
            tempContent['Source'] = "Content"
            time_url.append(tempContent)
        sorted_time_url = sorted(time_url, key=lambda time_url: time_url["CreationTime"])
        for items in time_url:
            tempkeyWord = dict()
            if "baidu" in urllib.parse.urlparse(items['Url']).netloc:
                try:
                    tempkeyWord['keyWord'] = urllib.parse.unquote_plus(items['Url'].split("wd=")[1].split("&")[0])
                    tempkeyWord['Time'] = items['CreationTime']
                except (KeyError, IndexError):
                    logger.critical("Couldn't parse key word!")
                    continue
            if "google" in urllib.parse.urlparse(items['Url']).netloc:
                try:
                    tempkeyWord['keyWord'] = urllib.parse.unquote_plus(items['Url'].split("q=")[1].split("&")[0])
                    tempkeyWord['Time'] = items['CreationTime']
                except (KeyError, IndexError):
                    logger.critical("Couldn't parse key word!")
                    continue
            if "bing" in urllib.parse.urlparse(items['Url']).netloc:
                try:
                    tempkeyWord['keyWord'] = urllib.parse.unquote_plus(items['Url'].split("q=")[1].split("&")[0])
                    tempkeyWord['Time'] = items['CreationTime']
                except (KeyError, IndexError):
                    logger.critical("Couldn't parse key word!")
                    continue
            else:
                continue
            keyWordList.append(tempkeyWord)
        sorted_keyWordList = sorted(keyWordList, key=lambda keyWordList: keyWordList["Time"])
        logger.critical(sorted_keyWordList)
