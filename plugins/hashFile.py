import hashlib
import multiprocessing
import os

from loguru import logger
from tqdm import tqdm


class hashFile:
    def __init__(self, inputFile):
        self.inputFile = inputFile

    def md5Hash(self):
        hash_md5 = hashlib.md5()
        filesize = os.path.getsize(self.inputFile)
        with tqdm(total=filesize, unit='B', unit_scale=True, miniters=1, desc="MD5 Hashing",
                  leave=False) as Bar:
            chunk_size = 128
            with open(self.inputFile, "rb") as inputFile:
                for chunk in iter(lambda: inputFile.read(chunk_size), b""):
                    hash_md5.update(chunk)
                    Bar.update(len(chunk))
                Bar.update(abs(filesize - Bar.n))
            logger.info("MD5 hash of file %s is %s" % (self.inputFile, hash_md5.hexdigest()))

    def sha256Hash(self):
        hash_sha256 = hashlib.sha256()
        filesize = os.path.getsize(self.inputFile)
        with tqdm(total=filesize, unit='B', unit_scale=True, miniters=1, desc="SHA256 Hashing",
                  leave=False) as Bar:
            chunk_size = 256
            with open(self.inputFile, "rb") as inputFile:
                for chunk in iter(lambda: inputFile.read(chunk_size), b""):
                    hash_sha256.update(chunk)
                    Bar.update(len(chunk))
                Bar.update(abs(filesize - Bar.n))
            logger.info("SHA256 hash of file %s is %s" % (self.inputFile, hash_sha256.hexdigest()))


def hashFile_MD5_SHA256(inputFile):
    a = hashFile(inputFile)
    pool = multiprocessing.Pool(2)
    pool.apply_async(a.md5Hash())
    pool.apply_async(a.sha256Hash())
    pool.close()
    pool.join()
