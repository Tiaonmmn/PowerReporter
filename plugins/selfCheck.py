import os
from pkgutil import iter_modules

import apt
from loguru import logger


class Checker:
    def __init__(self, name, package="", reason=""):
        self.name = name
        self.package = package
        self.reason = reason

    def find_command(self, cmd):
        fpath, fname = os.path.split(cmd)
        if fpath:
            return os.path.isfile(cmd) and os.access(cmd, os.X_OK)
        else:
            for p in os.environ['PATH'].split(os.pathsep):
                p = p.strip('"')
                fp = os.path.join(p, cmd)
                if os.path.isfile(fp) and os.access(fp, os.X_OK):
                    return True
        return False

    def checkCommand(self):
        if self.find_command(self.name):
            logger.info("Command %s found!" % self.name)
            return True
        else:
            logger.critical("Command %s not found!It's for %s usage." % (self.name, self.reason))
            return False

    def checkPackage(self):
        cache = apt.Cache()
        cache.update()
        cache.open(None)
        if cache[self.package].is_installed:
            logger.info("Package %s installed!" % self.package)
            return True
        else:
            logger.critical("Package %s not installed!" % self.package)
            return False

    def checkModule(self):
        if self.package in (name for loader, name, ispkg in iter_modules()):
            logger.info("Python module %s installed!" % self.package)
            return True
        else:
            logger.critical("Python module %s not installed!" % self.package)
            return False


def selfCheck():
    logger.info("Self checking necessary tools!")
    xmount = Checker("xmount", "xmount",
                     "Tool to crossmount between multiple input and output harddisk image files").checkCommand()
    ewfmount = Checker("ewfmount", "ewf-tools", "mount data stored in EWF files").checkCommand()
    affuse = Checker("affuse", "afflib-tools", "provide access to AFF containers").checkCommand()
    vmware_mount = Checker("vmware-mount", "VMware Workstation", "VMware DiskMount Utility").checkCommand()
    mountavfs = Checker("mountavfs", "avfs", "Compressed disk images").checkCommand()
    mmls = Checker("mmls", "sleuthkit",
                   "Displays the layout of a disk, including the unallocated spaces").checkCommand()
    fsstat = Checker("fsstat", "sleuthkit",
                     "Shows file system details and statistics including layout, sizes, and labels").checkCommand()
    file = Checker("file", "file", "determine file type").checkCommand()
    blkid = Checker("blkid", "util-linux", "locate/print block device attributes").checkCommand()
    parted = Checker("parted", "parted", "a partition manipulation program").checkCommand()
    disktype = Checker("disktype", "disktype", "disk format detector").checkCommand()
    mount_ntfs = Checker("mount.ntfs", "ntfs-3g", "Third Generation Read/Write NTFS Driver").checkCommand()
    lvm = Checker("lvm", "lvm2", "LVM2 tools").checkCommand()
    vmfs_fuse = Checker("vmfs-fuse", "vmfs-tools", "mount VMFS file system").checkCommand()
    mdadm = Checker("mdadm", "mdadm", "manage MD devices aka Linux Software RAID").checkCommand()
    cryptsetup = Checker("cryptsetup", "cryptsetup",
                         "manage plain dm-crypt and LUKS encrypted volumes").checkCommand()
    bdemount = Checker("bdemount", "libbde-utils",
                       "mounts a BitLocker Drive Encryption (BDE) encrypted volume").checkCommand()
    photorec = Checker("photorec", "testdisk",
                       "Recover lost files from harddisk, digital camera and cdrom").checkCommand()

    mount_squashfs = Checker("mount.squashfs", "squashfs-tools", "For squashfs volumes").checkPackage()
    mount_xfs = Checker("mount.xfs", "xfsprogs", "For XFS volumes").checkPackage()
    mount_jffs2 = Checker("mount.jffs2", "mtd-utils", "For JFFS2 volumes").checkPackage()
    progressbar = Checker("progressbar", "progressbar", "progress bar").checkModule()

    # results = [*locals()]
    result = locals()
    for key in result:
        if result[key] == False:
            logger.error("Missing %s command or package.Please install it manually!" % (key))
    logger.success("Self Check Done!")
