import os
import subprocess
from loguru import logger
import Evtx.Evtx
import Evtx.Views
from xml.dom.minidom import parseString
import xml.dom.minidom


class startTime:
    '''https://www.sans.org/reading-room/whitepapers/logging/evtx-windows-event-logging-32949'''

    def __init__(self, mountDir: str, volumeInfo: str, osVersion: str):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.osVersion = osVersion
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
        logger.error(findOutput)
        return findOutput

    def getSystemStartTime(self):
        logger.warning(
            "Showing System StartTime using Windows Event Log,but it may be inaccurate.Details seen in the paper!")
        if "Windows Vista" or "Windows 7" or "Windows 8" or "Windows 10" in self.osVersion:
            for eventFile in self.getEvtxFiles():
                with Evtx.Evtx(eventFile) as log:
                    for record in log.records():
                        domTree = parseString(record.xml())
                        id = domTree.documentElement.getElementsByTagName("EventID")[0].childNodes[0].data
                        if id == "6005":
                            time = domTree.documentElement.getElementsByTagName("TimeCreated")[0].getAttribute(
                                "SystemTime")
