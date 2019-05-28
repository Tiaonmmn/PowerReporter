__author__ = "Tiaonmmn.ZMZ"
import hashlib
import os
import platform
import sys
from loguru import logger
from tqdm import tqdm


class hashFile:
    def __init__(self, inputFile=None):
        self.inputFile = inputFile
        self.md5Hash = None
        self.sha256Hash = None

    def hashing(self):
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()
        hash_sha1 = hashlib.sha1()
        filesize = os.path.getsize(self.inputFile)
        with tqdm(total=filesize, unit='B', unit_scale=True, miniters=1, desc="Hashing Files",
                  leave=False) as Bar:
            if platform.system() == "Windows":
                chunk_size = 4096
            else:
                chunk_size = 128
            with open(self.inputFile, "rb") as inputFile:
                for chunk in iter(lambda: inputFile.read(chunk_size), b""):
                    hash_md5.update(chunk)
                    hash_sha256.update(chunk)
                    hash_sha1.update(chunk)
                    Bar.update(len(chunk))
                Bar.update(abs(filesize - Bar.n))
            logger.info("MD5 hash of file %s is %s" % (self.inputFile, hash_md5.hexdigest()))
            logger.info("SHA256 hash of file %s is %s" % (self.inputFile, hash_sha256.hexdigest()))
            logger.info("SHA1 hash of file %s is %s" % (self.inputFile, hash_sha1.hexdigest()))
            self.md5Hash = hash_md5.hexdigest()
            self.sha256Hash = hash_sha256.hexdigest()


def hashFile_MD5_SHA256(inputFile=None):
    a = hashFile(inputFile)
    a.hashing()


if __name__ == "__main__":
    hashFile_MD5_SHA256(sys.argv[1])
