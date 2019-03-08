import os
import unittest
from imagemounter import ImageParser


class FilesystemDirectMountTestBase(object):
    def test_mount(self):
        volumes = []
        self.filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.filename)
        parser = ImageParser([self.filename], None, False)
        for v in parser.init():
            self.assertIsNotNone(v.mountpoint)
            volumes.append(v)

        parser.force_clean()

        self.validate_count(volumes)
        self.validate_types(volumes)


class CramFSDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.cramfs'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "cramfs")


class ExtDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.ext3'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "ext")


class Fat12DirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.fat12'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "fat")


class IsoDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.iso'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "iso")


class MbrDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.mbr'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 13)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].flag, "meta")
        self.assertEqual(volumes[1].flag, "unalloc")
        self.assertEqual(volumes[2].fstype.type, "fat")
        self.assertEqual(volumes[3].fstype.type, "ext")
        self.assertEqual(volumes[4].fstype.type, "unknown")
        self.assertEqual(volumes[5].flag, "meta")
        self.assertEqual(volumes[6].flag, "meta")
        self.assertEqual(volumes[7].flag, "unalloc")
        self.assertEqual(volumes[8].fstype.type, "ext")
        self.assertEqual(volumes[9].flag, "meta")
        self.assertEqual(volumes[10].flag, "meta")
        self.assertEqual(volumes[11].flag, "unalloc")
        self.assertEqual(volumes[12].fstype.type, "fat")


class MinixDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.minix'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "minix")


class NtfsDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.ntfs'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "ntfs")


class SquashDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.sqsh'

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "squashfs")


class ZipDirectMountTest(FilesystemDirectMountTestBase, unittest.TestCase):
    def setUp(self):
        self.filename = 'images/test.zip'

    @unittest.skipIf(os.geteuid(), "requires root")
    def test_mount(self):
        super(ZipDirectMountTest, self).test_mount()

    def validate_count(self, volumes):
        self.assertEqual(len(volumes), 1)

    def validate_types(self, volumes):
        self.assertEqual(volumes[0].fstype.type, "iso")
