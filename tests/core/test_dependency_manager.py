import unittest
from unittest.mock import patch
from Javatar.core.dependency_manager import _DependencyManager


class TestDependencyManager(unittest.TestCase):
    @patch("os.path.exists", return_value=True)
    @patch(
        "Javatar.core.settings._Settings.get_global",
        return_value=["Alpha/Bravo/"]
    )
    @patch(
        "Javatar.core.settings._Settings.get_local",
        return_value=["Charlie/Delta/"]
    )
    def test_get_dependencies(self, *_):
        dm = _DependencyManager()
        self.assertEqual(
            dm.get_dependencies(from_global=True),
            [["Alpha/Bravo/", True]]
        )
        self.assertEqual(
            dm.get_dependencies(from_global=False),
            [["Charlie/Delta/", False], ["Alpha/Bravo/", True]]
        )
