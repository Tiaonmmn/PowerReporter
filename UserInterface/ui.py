import getopt
import os
import sys

from loguru import logger


class UI():
    def __init__(self, debug=False, verbose=0):
        self.debug = debug
        self.verbose = verbose

    def launch(self, modulesPaths=None):  # Any plugins must overwrite this method.
        print("This must be overwritten!")


class Usage():
    PROGRAM_USAGE = '''
PowerReporter --- An simple,easy,foolish forensic tool for my paper.\nCreated by Tiaonmmn.ZMZ.\nThis tool is using WTFPL License.Feel free to modify!
Please aware that this tool need root privilege!
Usage: ''' + sys.argv[0] + ''' [options]
Options:
    -v          --version           show program version.
    -h          --help              show this message.
    -c          --check             Check local system for necessary tools.
    -i          --input             Input image file.
    -m          --mountDir          Image mounting directory.(Default value:/tmp/)
    -o          --output            Output report related directory.(P.S. In unknown format.)
    -t          --tempDir           Directory to store temp file.(Default value:/tmp/)
'''
    VERSION = "2019.2"

    def __init__(self, argv):
        self.argv = argv
        self.debug = False
        self.verbose = 0
        self.inputFile = None
        self.outputDir = "/tmp"
        self.selfCheck = 0
        self.mountDir = "/tmp"
        self.tempDir = "/tmp"
        self.checkArgv()

    def checkArgv(self):
        if self.argv == []:  # If just call the program with no argv,self.argv will be [],not expect error.
            self.usage()
        try:
            opts, args = getopt.getopt(self.argv, "-h-v-i:-o:-c-m:-t:",
                                       ["help", 'version', "input=", "output=", "check",
                                        "mountDir=", "tempDir="])  # First only help message.
        except getopt.GetoptError:
            self.usage()
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
                exit(0)  # Help message
            if opt in ("-v", "--version"):  # version message.
                print("This is PowerReporter version " + self.VERSION + ".")
                exit(0)
            if opt in ("-i", "--input"):
                self.inputFile = arg
                if os.access(self.inputFile, os.F_OK):
                    if os.access(self.inputFile, os.R_OK):
                        logger.debug("inputFile check OK!")
                    else:
                        logger.error("Couldn't read file %s! Please check your permission!" % self.inputFile)
                        exit(-1)
                else:
                    logger.error("Couldn't find file %s! Please check your file!" % self.inputFile)
                    exit(-1)
            if opt in ("-o", "--output"):
                self.outputDir = arg
                if os.access(self.outputDir, os.R_OK | os.R_OK | os.W_OK):
                    pass
                else:
                    logger.error("Check your output directory!")
                    exit(-2)
            if opt in ("-c", "--check"):
                self.selfCheck = 1
            if opt in ("-m", "--mountDir"):
                self.mountDir = arg
                if os.access(self.mountDir, os.F_OK | os.R_OK | os.W_OK):
                    logger.debug("mountDir check OK!")
                else:
                    logger.error("The mountDir %s doesn't have enough permission!Please check it!" % self.mountDir)
                    exit(-3)
            if opt in ("-t", "--tempDir"):
                self.tempDir = arg
                if os.access(self.mountDir, os.F_OK | os.R_OK | os.W_OK):
                    logger.debug("tempDir check OK!")
                else:
                    logger.error("The tempDir %s doesn't have enough permission!Please check it!" % self.tempDir)
                    exit(-3)
        return

    def usage(self):
        print(self.PROGRAM_USAGE)
        exit(0)
