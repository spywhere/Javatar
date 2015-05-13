import unittest
from unittest.mock import patch
from Javatar.core.java_utils import JavaUtils


class TestJavaUtils(unittest.TestCase):
    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=True
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha/"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo/"
    )
    def test_to_readable_class_path_default(self, *_):
        self.assertEqual(
            JavaUtils().to_readable_class_path("alpha"),
            "(Default Package)"
        )

    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=False
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha/"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo/"
    )
    def test_to_readable_class_path_unknown(self, *_):
        self.assertEqual(
            JavaUtils().to_readable_class_path("alpha"),
            "(Unknown Package)"
        )

    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=True
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha/"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo/charlie/"
    )
    def test_to_readable_class_path_normal(self, *_):
        self.assertEqual(
            JavaUtils().to_readable_class_path("alpha/bravo/charlie"),
            "bravo.charlie"
        )

    def test_is_class_path_invalid(self):
        tests = [
            ".alpha", "alpha.", ".alpha.bravo", "alpha.bravo.", "alpha:,",
            "alpha<,", "alpha:,<,", "alpha<,:,", "alpha:", "alpha<", "alpha:<",
            "alpha<:", "alpha:bravo,", "alpha<bravo,", "alpha<bravo,:charlie",
            "alpha:bravo,:charlie", "alpha:bravo<charlie,",
            "alpha<bravo:charlie,", "alpha:bravo", "alpha:bravo<charlue",
            "alpha<bravo:charlie", "alpha:bravo,charlie", "alpha<bravo,charlie",
            "alpha:bravo,charlie<delta", "alpha<bravo,charlie:delta",
            "alpha:bravo,charlie<delta,echo", "alpha<bravo,charlie:delta,echo"
        ]

        for test in tests:
            self.assertEqual(
                JavaUtils().is_class_path(test, special=False),
                False
            )

    def test_is_class_path(self):
        tests = [
            "alpha", "alpha.bravo", "alpha.bravo.charlie"
        ]

        for test in tests:
            self.assertEqual(
                JavaUtils().is_class_path(test, special=False),
                True
            )

    def test_is_class_path_invalid_special(self):
        tests = [
            ".alpha", "alpha.", ".alpha.bravo", "alpha.bravo.", "alpha:,",
            "alpha<,", "alpha:,<,", "alpha<,:,", "alpha:", "alpha<", "alpha:<",
            "alpha<:", "alpha:bravo,", "alpha<bravo,", "alpha<bravo,:charlie",
            "alpha:bravo,:charlie", "alpha:bravo<charlie,",
            "alpha<bravo:charlie,"
        ]

        for test in tests:
            self.assertEqual(
                JavaUtils().is_class_path(test, special=True),
                False
            )

    def test_is_class_path_special(self):
        tests = [
            "alpha", "alpha.bravo", "alpha.bravo.charlie", "alpha:bravo",
            "alpha:bravo<charlue", "alpha<bravo:charlie", "alpha:bravo,charlie",
            "alpha<bravo,charlie", "alpha:bravo,charlie<delta",
            "alpha<bravo,charlie:delta", "alpha:bravo,charlie<delta,echo",
            "alpha<bravo,charlie:delta,echo"
        ]

        for test in tests:
            self.assertEqual(
                JavaUtils().is_class_path(test, special=True),
                True
            )

    def test_normalize_package_path(self):
        tests = [
            "alpha", "alpha.", ".alpha", "alpha..", "..alpha", ".alpha.",
            "..alpha.."
        ]

        for test in tests:
            self.assertEqual(
                JavaUtils().normalize_package_path(test),
                "alpha"
            )

        tests = [
            "alpha.bravo", "alpha.bravo.", ".alpha.bravo", "alpha.bravo..",
            "..alpha.bravo", ".alpha.bravo.", "..alpha.bravo.."
        ]

        for test in tests:
            self.assertEqual(
                JavaUtils().normalize_package_path(test),
                "alpha.bravo"
            )

    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha/"
    )
    def test_to_package(self, *_):
        self.assertEqual(
            JavaUtils().to_package(
                "alpha/"
            ).as_class_path(),
            ""
        )
        self.assertEqual(
            JavaUtils().to_package(
                "alpha/bravo/"
            ).as_class_path(),
            "bravo"
        )
        self.assertEqual(
            JavaUtils().to_package(
                "alpha/bravo/charlie/"
            ).as_class_path(),
            "bravo.charlie"
        )
        self.assertEqual(
            JavaUtils().to_package(
                "alpha/",
                relative=False
            ).as_class_path(),
            "alpha"
        )
        self.assertEqual(
            JavaUtils().to_package(
                "alpha/bravo/",
                relative=False
            ).as_class_path(),
            "alpha.bravo"
        )
        self.assertEqual(
            JavaUtils().to_package(
                "alpha/bravo/charlie/",
                relative=False
            ).as_class_path(),
            "alpha.bravo.charlie"
        )
