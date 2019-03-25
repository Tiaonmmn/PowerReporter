import os
import compoundfiles
from striprtf.striprtf import rtf_to_text
import magic
import datetime
from Registry import Registry
from loguru import logger


class miscFiles:
    def __init__(self, mountDir: str, volumeInfo: str, bias):
        self.mountDir = mountDir
        self.volumeInfo = volumeInfo
        self.bias = bias

    def parseStickNotes(self):
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
                if os.access("{0}/AppData/Roaming/Microsoft/Sticky Notes/StickyNotes.snt".format(userDir), os.F_OK | os.R_OK):
                    pass
                else:
                    logger.warning("Couldn't find StickNotes file on %s" % userDir)
                    continue
                doc = compoundfiles.CompoundFileReader(
                    "{0}/AppData/Roaming/Microsoft/Sticky Notes/StickyNotes.snt".format(userDir))
                for item in doc:
                    if item.isdir:
                        logger.info("Directory name: {0}.".format(item.name))
                        logger.info("Directory last modified time: {0}.".format(item.modified))
                        for sub_item in item:
                            content = doc.open(sub_item).read()
                            logger.info("Entry name: {0}.".format(sub_item.name))
                            if "Rich Text" in magic.from_buffer(content):
                                logger.debug("This is an RTF file.Stripping to normal text.")
                                logger.info("Entry content: {0}.".format(rtf_to_text(content.decode())))
                            else:
                                logger.info("Entry type: {0}.".format(magic.from_buffer(doc.open(sub_item).read())))
                                logger.info("Entry content: {0}.".format(content))
                    elif item.isfile:
                        logger.info("Entry name: {0}.".format(item.name))
                        logger.info("Entry content: {0}.".format(doc.open(item).read()))
                        logger.info("Entry type: {0}.".format(magic.from_buffer(doc.open(item).read())))
                    else:
                        continue
