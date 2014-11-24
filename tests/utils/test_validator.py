import sublime
import unittest
from unittest.mock import patch

from javatar.utils.javatar_validator import is_package


class TestValidator(unittest.TestCase):
    @patch('javatar.utils.javatar_utils.get_settings')
    def test_is_package(self, get_settings):
        get_settings.return_value = sublime.load_settings(
            "Javatar.sublime-settings"
        ).get('package_name_match')

        self.assertTrue(
            is_package('hello.world')
        )

    @patch('javatar.utils.javatar_utils.get_settings')
    def test_is_package_special(self, get_settings):
        get_settings.return_value = sublime.load_settings(
            "Javatar.sublime-settings"
        ).get('special_package_name_match')

        self.assertTrue(
            is_package('hello.world,')
        )
