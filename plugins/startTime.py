import os
import subprocess
from loguru import logger
import Evtx.Evtx as evtx
from xml.dom.minidom import parseString
import copy
import datetime
import xml


class startTime:
    '''https://www.sans.org/reading-room/whitepapers/logging/evtx-windows-event-logging-32949'''

    def __init__(self, mountDir: str, volumeInfo: str, osVersion: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.osVersion = osVersion
        self.bias = bias
        self.EvtxList = self.getEvtxFiles()
        pass

    def getEvtxFiles(self):
        findOutput = []
        output = self.volumeInfo
        if "FAT" or "NTFS" in output.split(" ")[0]:
            os.chdir("%s/%s" % (self.mountDir, output.split(" ")[2]))
        else:
            return None
        if "Windows Vista" or "Windows 7" or "Windows 8" or "Windows 10" in self.osVersion:
            for line in subprocess.getoutput("find . -name *.evtx -print").splitlines():
                findOutput.append(line)
        else:
            for line in subprocess.getoutput("find . -name *.evt -print").splitlines():
                findOutput.append(line)
        return findOutput

    def getLastSystemStartTime(self):
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        lastTime = None
        logger.warning(
            "Now Showing System StartTime using Windows Event Log,but it may be inaccurate.Details seen in the paper!")
        if "Windows Vista" or "Windows 7" or "Windows 8" or "Windows 10" in self.osVersion:
            for eventFile in self.EvtxList:
                with evtx.Evtx(eventFile) as log:
                    logger.debug("Processing {0} file!".format(eventFile))
                    for record in log.records():
                        domTree = parseString(record.xml())
                        id = domTree.documentElement.getElementsByTagName("EventID")[0].childNodes[0].data
                        if id == "6005":
                            time = domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                "SystemTime")
                            if lastTime is None:
                                lastTime = domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                    "SystemTime")
                            if time < lastTime:
                                pass
                            else:
                                lastTime = copy.deepcopy(time)

        if lastTime is None:
            logger.warning("Couldn't find system start time!")
        else:
            lastTime = (datetime.datetime.strptime(lastTime, "%Y-%m-%d %H:%M:%S") + bias).strftime(
                "%Y %m %d - %H:%M:%S")
            logger.info("Last system start time(Event Log Service start time) is: %s" % lastTime)

    def getSystemStartTimeLog(self):
        try:
            bias = datetime.timedelta(hours=-self.bias)
        except TypeError:
            pass
        realResult = []  # TODO:realResult is a list contains multiple dicts
        logger.warning(
            "Now Showing System StartTime using Windows Event Log,but it may be inaccurate.Details seen in the paper!")
        if "Windows Vista" or "Windows 7" or "Windows 8" or "Windows 10" in self.osVersion:
            for eventFile in self.EvtxList:
                with evtx.Evtx(eventFile) as log:
                    logger.debug("Processing {0} file!".format(eventFile))
                    for record in log.records():
                        domTree = parseString(record.xml())
                        id = domTree.documentElement.getElementsByTagName("EventID")[0].childNodes[0].data
                        if id == "4608":  # Security event.Windows is starting up
                            tempResult = dict()
                            startUpTime = (datetime.datetime.strptime(
                                domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                    "SystemTime"), "%Y-%m-%d %H:%M:%S.%f") + bias).strftime("%Y %m %d - %H:%M:%S")
                            tempResult["Starting up"] = startUpTime
                            realResult.append(tempResult)
                        if id == "4624":  # Security event.Successfully logon.
                            tempResult = dict()
                            startUpTime = (datetime.datetime.strptime(
                                domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                    "SystemTime"), "%Y-%m-%d %H:%M:%S.%f") + bias).strftime("%Y %m %d - %H:%M:%S")
                            tempResult["Successfully logon"] = startUpTime
                            list = domTree.documentElement.getElementsByTagName("EventData")[0].childNodes
                            for a in list:
                                if type(a) != xml.dom.minidom.Text and a.getAttribute("Name") == "TargetUserName":
                                    if "SYSTEM" or "SERVICE" or "ANONYMOUS" in a.childNodes[0].data:
                                        continue
                                    tempResult["Username"] = a.childNodes[0].data
                            realResult.append(tempResult)
                        if id == "1100":  # Security event.Eventlog Service is shuttindg down
                            tempResult = dict()
                            startUpTime = (datetime.datetime.strptime(
                                domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                    "SystemTime"), "%Y-%m-%d %H:%M:%S.%f") + bias).strftime("%Y %m %d - %H:%M:%S")
                            tempResult["Shutting down"] = startUpTime
                            realResult.append(tempResult)
                        if id == "4647":  # Security event.Logon off
                            tempResult = dict()
                            startUpTime = (datetime.datetime.strptime(
                                domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                    "SystemTime"), "%Y-%m-%d %H:%M:%S.%f") + bias).strftime("%Y %m %d - %H:%M:%S")
                            tempResult["Logon off"] = startUpTime
                            list = domTree.documentElement.getElementsByTagName("EventData")[0].childNodes
                            for a in list:
                                if type(a) != xml.dom.minidom.Text and a.getAttribute("Name") == "TargetUserName":
                                    tempResult["Username"] = a.childNodes[0].data
                            realResult.append(tempResult)
                        if id == "4625":  # Security event.Logon failure.
                            tempResult = dict()
                            startUpTime = (datetime.datetime.strptime(
                                domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                    "SystemTime"), "%Y-%m-%d %H:%M:%S") + bias).strftime("%Y %m %d - %H:%M:%S")
                            tempResult["Logon failure"] = startUpTime
                            list = domTree.documentElement.getElementsByTagName("EventData")[0].childNodes
                            for a in list:
                                if type(a) != xml.dom.minidom.Text and a.getAttribute("Name") == "TargetUserName":
                                    tempResult["Username"] = a.childNodes[0].data
                            realResult.append(tempResult)
        logger.error(realResult)
