import unittest
from unittest.mock import patch


class TestUtils(unittest.TestCase):
    def test_get_package_root_dir(self):
        ...

    # @patch('')
    def test_to_package(self):
        from Javatar.utils.javatar_utils import to_package

        self.assertEquals(
            to_package('org/google/search', False),
            'org.google.search'
        )
