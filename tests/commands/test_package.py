import os
from os.path import join
import tempfile
import unittest
from unittest.mock import MagicMock

from javatar.commands.javatar_package import JavatarCreateJavatarPackageCommand


class TestPackageFolderTests(unittest.TestCase):
    def setUp(self):
        # create test directories
        directory = tempfile.mkdtemp()
        hello = join(directory, 'hello')
        derpy_derp = join(directory, 'derpy_derp')
        world = join(derpy_derp, 'world')
        invalid = join(derpy_derp, '.invalid')
        for direct in [hello, derpy_derp, world, invalid]:
            os.mkdir(direct)

        self.folders = [hello, world, invalid, derpy_derp, directory]

    def tearDown(self):
        # cleanup after test
        for direct in self.folders:
            os.rmdir(direct)

    def test_get_source_folder(self):
        window = MagicMock()
        inst = JavatarCreateJavatarPackageCommand(window)

        # test directories created, run test
        self.assertEqual(
            inst.get_source_folder(self.folders[-1]),
            [
                ['derpy_derp', join(self.folders[-1], 'derpy_derp')],
                ['world', join(self.folders[-1], 'derpy_derp', 'world')],
                ['hello', join(self.folders[-1], 'hello')]
            ]
        )

    # def test_is_source_folder_not_can_empty(self):
    #     ...

    def test_get_filename(self):
        window = MagicMock()
        inst = JavatarCreateJavatarPackageCommand(window)

        inst.package_info = ['Java Standard Edition 8']
        self.assertEqual(
            inst.get_filename(),
            'JavaSE8'
        )

        inst.package_info = ['Bukkit 1.7.2 R0.3 Beta Build']
        self.assertEqual(
            inst.get_filename(),
            'Bukkit-1.7.2-R0.3-BB'
        )
