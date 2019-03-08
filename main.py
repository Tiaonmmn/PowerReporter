#!/usr/bin/python3
'''
Firstly,it's a really simple,foolish,easy toy.
For Paper!
I don't implement any console or graphical interface.Just give me an image,I will give you a report.
Questions are based on Meiyapico's Forensic Contest.No additional work.
It's heavily based on Digital Forensic Framework.Thanks for the work.(Although it's not updated any more.)
We don't implement dynamic module loading for now.
Now,we have an idea of directly mount the image and search for info,which requires for many loads of disk space.

'''

import os
import sys

from loguru import logger
from tqdm import tqdm

from UserInterface.ui import Usage
from plugins import *

if __name__ == "__main__":
    argv = Usage(sys.argv[1:])
    if os.geteuid() != 0:
        exit(
            "You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    if argv.selfCheck == 1:
        selfCheck.selfCheck()
        exit(0)
    else:
        mounting.mountImage(inputFile=argv.inputFile, mountDir=argv.mountDir)
        # TODO:Fuck images!!!!!!
        logger.critical("Now let's do this!")
        bar = tqdm(total=12)  # TODO: Modify this!!!
        logger.info("Step 1.Hashing files.")
        logger.warning(
            "This step may take much time,you can hash your images later manually.Do you still want to do this?[Y/N]")
        if input() == 'Y':
            hashFile.hashFile_MD5_SHA256(argv.inputFile)
        bar.update(1)
        osVersion = detectOS.detectOperationSystem(inputFile=argv.inputFile, mountDir=argv.mountDir)
        bar.update(1)

        mounting.unmountImage()
