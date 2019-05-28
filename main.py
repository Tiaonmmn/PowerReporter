#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Firstly,it's a really simple,foolish,easy toy.
For Paper!
I don't implement any console or graphical interface.Just give me an image,I will give you a report.
Questions are based on Meiyapico's Forensic Contest.No additional work.
It's heavily based on Digital Forensic Framework.Thanks for the work.(Although it's not updated any more.)
We don't implement dynamic module loading for now.
Now,we have an idea of directly mount the image and search for info,which requires for many loads of disk space.

'''

__author__ = "Tiaonmmn.ZMZ"
import os
import random
import subprocess
import sys
import hashlib
import csv
from stat import S_ISFIFO
from UserInterface import selfCheck
from UserInterface.ui import Usage

from multiprocessing import *

if __name__ == "__main__":
    global count
    count = 0
    argv = Usage(sys.argv[1:])
    if os.geteuid() != 0:
        exit(
            "You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    if argv.selfCheck == 1:
        selfCheck.selfCheck()
        exit(0)
    from loguru import logger
    from tqdm import tqdm
    from plugins import *
    from browser import *

    umountOutput = subprocess.getoutput(os.path.dirname(os.path.realpath(__file__)) + "/imagemounter/imount.py -u")
    if "[+] Nothing to do" in umountOutput:
        pass
    else:
        subprocess.getoutput(os.path.dirname(os.path.realpath(__file__)) + "/imagemounter/imount.py -u")
    volumeInfo = mounting.mountImage(inputFile=argv.inputFile, mountDir=argv.mountDir).getVolumeDirectory()
    # TODO:Fuck images!!!!!!
    logger.critical("Now let's do this!")
    bar = tqdm(total=1 + len(volumeInfo) * random.randint(1, 100))  # TODO: Modify this!!!
    count += 1
    # logger.info("Step %d.Hashing files." % count)
    # logger.warning(
    #     "This step may take much time,you can hash your images later manually.Do you still want to do this?[Y/N]")
    # if input().upper() == 'Y':
    #     hashFile.hashFile_MD5_SHA256(argv.inputFile)
    # bar.update(1)
    if len(volumeInfo) > 1:
        logger.critical("Image file has multiple volumes.And we should check them one by one.")
    else:
        logger.critical("Image file has single volume.We are working on it.")


    def main1():
        global count
        for volume in volumeInfo:
            logger.error("showing volume %s" % volume)
            count += 1
            logger.info("Step %d.Detecting Operating System on volume %s." % (count, volume.split(" ")[1]))
            osVersion = detectOS.detectOperationSystem(volumeInfo=volume,
                                                       mountDir=argv.mountDir)
            bar.update(1)

            count += 1
            logger.info("Step %d.Showing Time Zone Info on volume %s." % (count, volume.split(" ")[1]))
            timezoneInfo.timezoneInfo(volumeInfo=volume,
                                      mountDir=argv.mountDir).getTimeZoneInfo()
            bias = timezoneInfo.timezoneInfo(volumeInfo=volume,
                                             mountDir=argv.mountDir).getTimeZoneBias()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing User Shell Folder info on volume %s." % (count, volume.split(" ")[1]))
            customShellFolder.customShellFolder(mountDir=argv.mountDir, volumeInfo=volume).getCustomShellFolder()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Computer Name Info on volume %s." % (count, volume.split(" ")[1]))
            computerName.computerName(volumeInfo=volume,
                                      mountDir=argv.mountDir).showComputerName()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing User Account Info on volume %s." % (count, volume.split(" ")[1]))
            samParse.userAccountParse(mountDir=argv.mountDir, volumeInfo=volume)
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Last Logged User Info on volume %s." % (count, volume.split(" ")[1]))
            lastLogon.lastLogon(mountDir=argv.mountDir, volumeInfo=volume).getLastLoggedInfo()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Last System Start Time on volume %s." % (count, volume.split(" ")[1]))
            start = startTime.startTime(mountDir=argv.mountDir, volumeInfo=volume, osVersion=osVersion,
                                        bias=bias)
            start.getLastSystemStartTime()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Last System Start Time on volume %s." % (count, volume.split(" ")[1]))
            start.getSystemStartTimeLog()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Last System Start Time on volume %s." % (count, volume.split(" ")[1]))
            printers.printers(mountDir=argv.mountDir, volumeInfo=volume).showPrintersInfo()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Last System Shutdown Time on volume %s." % (count, volume.split(" ")[1]))
            shutdownTime.shutdownTime(mountDir=argv.mountDir, volumeInfo=volume, bias=bias).getLastShutdownTime()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Network Device Information on volume %s." % (count, volume.split(" ")[1]))
            networkDevice.networkDevice(mountDir=argv.mountDir, volumeInfo=volume).getNetworkDeviceInfo()
            bar.update(1)
            count += 1
            logger.info(
                "Step %d.Showing Operating System Installed Date Information on volume %s." % (
                    count, volume.split(" ")[1]))
            osInstalledTime.osInstalledTime(mountDir=argv.mountDir, volumeInfo=volume, bias=bias).getOSInstalledTime()
            bar.update(1)
            count += 1
            logger.info(
                "Step %d.Showing Operating System Installed Applications Information on volume %s." % (
                    count, volume.split(" ")[1]))
            installedSoftware.installedSoftware(mountDir=argv.mountDir,
                                                volumeInfo=volume).getInstalledSoftwareInfoWin64()
            installedSoftware.installedSoftware(mountDir=argv.mountDir,
                                                volumeInfo=volume).getInstalledSoftwareInfoWin32()
            bar.update(1)
            count += 1
            logger.info(
                "Step %d.Showing Windows Prefetch File Information on volume %s." % (count, volume.split(" ")[1]))
            applicationExecutionLog.applicationExecutionLog(mountDir=argv.mountDir,
                                                            volumeInfo=volume, bias=bias).getLastExecutionByPrefetch()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Windows Shim Cache Information on volume %s." % (count, volume.split(" ")[1]))
            applicationExecutionLog.applicationExecutionLog(mountDir=argv.mountDir,
                                                            volumeInfo=volume, bias=bias).parse_shimCacheParser_Output()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Windows UserAssist Information on volume %s." % (count, volume.split(" ")[1]))
            applicationExecutionLog.applicationExecutionLog(mountDir=argv.mountDir,
                                                            volumeInfo=volume, bias=bias).getUserAssistInfo()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing IE info on volume %s." % (count, volume.split(" ")[1]))
            InternetExplorer = IE.IE(volumeInfo=volume, mountDir=argv.mountDir, tempDir=argv.tempDir)
            InternetExplorer.getIEVersion()
            InternetExplorer.getIEContent()
            InternetExplorer.getIEHistory()
            InternetExplorer.getIECookies()
            InternetExplorer.getIEKeyWords()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing old IE info on volume %s." % (count, volume.split(" ")[1]))
            oldInternetExplorer = oldIE.IE(volumeInfo=volume, mountDir=argv.mountDir, tempDir=argv.tempDir,
                                           osVersion=osVersion)
            oldInternetExplorer.getTypedURL()
            oldInternetExplorer.getIEHistory()
            oldInternetExplorer.getIECookies()
            oldInternetExplorer.getIEContents()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing IE info on volume %s." % (count, volume.split(" ")[1]))
            Explorer.Explorer(mountDir=argv.mountDir, volumeInfo=volume, bias=bias,
                              outputDir=argv.outputDir).getKeyWordAtSearchbar()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Outlook info on volume %s." % (count, volume.split(" ")[1]))
            outlook = Office.Office(mountDir=argv.mountDir, volumeInfo=volume, bias=bias, tempDir=argv.tempDir)
            outlook.getOfficeFileMRU()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing USB info on volume %s." % (count, volume.split(" ")[1]))
            usbInfo.usbInfo(mountDir=argv.mountDir, volumeInfo=volume, bias=bias).getUsbVolumeName()
            bar.update(1)
            count += 1
            logger.info("Step %d.Showing Shellbag info on volume %s." % (count, volume.split(" ")[1]))
            explorer = Explorer.Explorer(mountDir=argv.mountDir, volumeInfo=volume, bias=bias, outputDir=argv.outputDir)
            explorer.getShellBag()
            explorer.getMapNetworkDriveMRU()
            explorer.getRunMRU()
            explorer.getJumpList()
            explorer.showDesktopFiles()
            explorer.extractThumbCacheFiles()
            bar.update(1)

            count += 1
            logger.info("Step %d.Parsing sticky notes info on volume %s." % (count, volume.split(" ")[1]))
            miscFiles.miscFiles(mountDir=argv.mountDir, volumeInfo=volume, bias=bias).parseStickNotes()
            bar.update(1)
            # os.chdir(os.path.dirname(os.path.realpath(__file__)))
            # os.system("lsof|grep %s"%argv.mountDir)
            # mounting.unmountImage(argv.mountDir)


    def main2():
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()
        hash_sha1 = hashlib.sha1()
        logger.info("Now we are hashing files on the disk!")
        csvfile = open(argv.outputDir + "/" + "filehash.csv", 'a')
        csvwriter = csv.writer(csvfile, dialect=("excel"))
        csvwriter.writerow(["File Fullpath", "MD5 Hash", "SHA1 Hash", "SHA256 Hash"])
        for volume in volumeInfo:
            for parent, dirnames, filenames in os.walk(argv.mountDir + "/" + volume.split(" ")[-1], followlinks=False):
                for filename in filenames:
                    file_path = os.path.join(parent, filename)
                    if S_ISFIFO(os.stat(file_path).st_mode):
                        continue
                    try:
                        with open(file_path, "rb") as inputFile:
                            for chunk in iter(lambda: inputFile.read(4096), b""):
                                hash_md5.update(chunk)
                                hash_sha256.update(chunk)
                                hash_sha1.update(chunk)
                    except FileNotFoundError:
                        logger.critical("Error getting file %s content." % file_path)
                        continue
                    csvwriter.writerow(
                        [file_path, hash_md5.hexdigest(), hash_sha256.hexdigest(), hash_sha1.hexdigest()])


    p2 = Process(target=main2)
    p1 = Process(target=main1)
    p2.start()
    p1.start()
