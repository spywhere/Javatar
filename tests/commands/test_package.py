from os.path import join
from unittest.mock import MagicMock, patch
import os
import re
import sublime
import tempfile
import unittest

from Javatar.commands.javatar_package import JavatarCreateJavatarPackageCommand


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


class TestPackageCommand(unittest.TestCase):
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

    @patch('Javatar.commands.javatar_package.JavatarCreateJavatarPackageCommand.finalize_package')
    @patch('Javatar.commands.javatar_package.JavatarCreateJavatarPackageCommand.is_doclet_folder')
    @patch('Javatar.commands.javatar_package.get_project_dir')
    @patch('Javatar.commands.javatar_package.get_source_folder')
    @patch('sublime_api.window_run_command')
    @patch('sublime.active_window')
    def test_on_complete(self, active_window, window_run_command, get_source_folder, get_project_dir, is_doclet_folder, finalize_package):
        window = MagicMock(spec=sublime.Window)
        get_project_dir.return_value = tempfile.mkdtemp()
        os.mkdir(join(get_project_dir.return_value, 'blah'))
        is_doclet_folder.return_value = True
        get_source_folder.return_value = ''

        inst = JavatarCreateJavatarPackageCommand(window)

        inst.package_info = [
            'Name',
            'Filename',
            'Conflicts',
            [
                None,
                '/blah'
            ]
        ]

        inst.on_complete()

        output = finalize_package.mock_calls[0][1][0]

        # Different platform generate different file name
        # so use regular expression to match the file name
        # expected regular expressions (per line)
        expected = (
            r'## Javatar Packages report',
            r'\* Package name: Name',
            r'\* Package filename: Filename',
            r'\* Package conflicts: Conflicts',
            r'## Generated Packages',
            r'',
            r'## Package Info',
            r'',
            r'\* Output file: .*',
            r''
        )

        outputs = output.split('\n')
        self.assertEqual(len(outputs), len(expected))
        for i in range(len(expected)):
            output = outputs[i]
            expect = expected[i]
            self.assertIsNotNone(re.match(expect, output))

        cmd = active_window.return_value.run_command.mock_calls[0][1][1]['shell_cmd']

        # expected regular expressions (per command)
        expected = (
            r'cd .+',
            r'echo Generating\.\.\.',
            r'javadoc -sourcepath blah -docletpath .+ '
            r'-name Name -doclet me\.spywhere\.doclet\.Javatar -quiet ',
            r'echo Done'
        )

        cmds = cmd.split(";")
        self.assertEqual(len(cmds), len(expected))
        # check them one by one
        for i in range(len(expected)):
            cmd = cmds[i]
            expect = expected[i]
            self.assertIsNotNone(re.match(expect, cmd))

        os.rmdir(join(get_project_dir.return_value, 'blah'))
        os.removedirs(get_project_dir.return_value)
