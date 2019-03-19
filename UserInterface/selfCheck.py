import os
from pkgutil import iter_modules

import apt
from loguru import logger


class Checker:
    def __init__(self, name="", package="", reason=""):
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
            logger.critical(
                "Command %s not found!It's for %s usage in %s package." % (self.name, self.reason, self.package))
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
    xmount = Checker(name="xmount", package="xmount",
                     reason="Tool to crossmount between multiple input and output harddisk image files").checkCommand()
    ewfmount = Checker(name="ewfmount", package="ewf-tools", reason="mount data stored in EWF files").checkCommand()
    affuse = Checker(name="affuse", package="afflib-tools", reason="provide access to AFF containers").checkCommand()
    vmware_mount = Checker(name="vmware-mount", package="VMware Workstation",
                           reason="VMware DiskMount Utility").checkCommand()
    mountavfs = Checker(name="mountavfs", package="avfs", reason="Compressed disk images").checkCommand()
    mmls = Checker(name="mmls", package="sleuthkit",
                   reason="Displays the layout of a disk, including the unallocated spaces").checkCommand()
    fsstat = Checker(name="fsstat", package="sleuthkit",
                     reason="Shows file system details and statistics including layout, sizes, and labels").checkCommand()
    file = Checker(name="file", package="file", reason="determine file type").checkCommand()
    blkid = Checker(name="blkid", package="util-linux", reason="locate/print block device attributes").checkCommand()
    parted = Checker(name="parted", package="parted", reason="a partition manipulation program").checkCommand()
    disktype = Checker(name="disktype", package="disktype", reason="disk format detector").checkCommand()
    mount_ntfs = Checker(name="mount.ntfs", package="ntfs-3g",
                         reason="Third Generation Read/Write NTFS Driver").checkCommand()
    lvm = Checker(name="lvm", package="lvm2", reason="LVM2 tools").checkCommand()
    vmfs_fuse = Checker(name="vmfs-fuse", package="vmfs-tools", reason="mount VMFS file system").checkCommand()
    mdadm = Checker(name="mdadm", package="mdadm", reason="manage MD devices aka Linux Software RAID").checkCommand()
    cryptsetup = Checker(name="cryptsetup", package="cryptsetup",
                         reason="manage plain dm-crypt and LUKS encrypted volumes").checkCommand()
    bdemount = Checker(name="bdemount", package="libbde-utils",
                       reason="mounts a BitLocker Drive Encryption (BDE) encrypted volume").checkCommand()
    photorec = Checker(name="photorec", package="testdisk",
                       reason="Recover lost files from harddisk, digital camera and cdrom").checkCommand()
    samdump2 = Checker(name="samdump2", package="samdump2",
                       reason="retrieves syskey and extract hashes from Windows 2k/NT/XP/Vista SAM.").checkCommand()
    esedbinfo = Checker(name="esedbinfo", package="libesedb-utils",
                        reason="determines information about an Extensible Storage Engine(ESE) Database File (EDB)").checkCommand()
    esedbexport = Checker(name="esedbexport", package="libesedb-utils",
                          reason="Extract ESE Database.").checkCommand()
    pasco = Checker(name="pasco", package="pasco",
                    reason="tool to extract information from MS IE cache files.").checkCommand()
    msiecfinfo = Checker(name="msiecfinfo", package="libmsiecf-utils",
                         reason="determines information about a MSIE Cache File (index.dat).").checkCommand()

    mount_squashfs = Checker(name="mount.squashfs", package="squashfs-tools",
                             reason="For squashfs volumes").checkPackage()
    mount_xfs = Checker(name="mount.xfs", package="xfsprogs", reason="For XFS volumes").checkPackage()
    mount_jffs2 = Checker(name="mount.jffs2", package="mtd-utils", reason="For JFFS2 volumes").checkPackage()

    progressbar = Checker(name="progressbar", package="progressbar", reason="progress bar").checkModule()
    tqdm = Checker(name="tqdm", package="tqdm", reason="progress bar").checkModule()
    registry = Checker(name="python-registry", package="Registry",
                       reason="Python parser of Windows registry").checkModule()
    termcolor = Checker(name="termcolor", package="termcolor", reason="terminal color").checkModule()
    evtx = Checker(name="python-Evtx", package="Evtx", reason="Parser for Windows new version event logs").checkModule()
    # results = [*locals()]
    result = locals()
    for key in result:
        if not result[key]:
            logger.error("Missing %s command or package.Please install it manually!" % (key))
    logger.success("Self Check Done!")
