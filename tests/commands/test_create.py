import sublime
import unittest
from unittest.mock import patch, MagicMock
from Javatar.commands.creates import (
    JavatarCreateCommand,
    JavatarCreatePackageCommand
)


class TestCreateClass(unittest.TestCase):
    @patch(
        "sublime.Window.folders",
        return_value=[]
    )
    @patch(
        "sublime.Window.active_view",
        return_value=None
    )
    def test_parse_create_invalid_location(self, *_):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)

        tests = [
            "", "~", ":", "<", ":<", "<:", "alpha.", ".alpha", ".alpha.",
            "alpha.bravo.", ".alpha.bravo", ".alpha.bravo.", ":charlie",
            "<charlie", ":charlie,delta", "<charlie,delta"
        ]

        for test in tests:
            self.assertEqual(
                cmd.parse_create(test),
                "Cannot specify package location"
            )
            self.assertEqual(
                cmd.parse_create("~" + test),
                "Cannot specify package location"
            )

    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=True
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo"
    )
    def test_parse_create_invalid_name(self, *_):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)

        tests = [
            "", "~", ":", "<", ":<", "<:", "alpha.", ".alpha", ".alpha.",
            "alpha.bravo.", ".alpha.bravo", ".alpha.bravo.", ":charlie",
            "<charlie", ":charlie,delta", "<charlie,delta"
        ]

        for test in tests:
            self.assertEqual(
                cmd.parse_create(test),
                "Invalid class naming"
            )
            self.assertEqual(
                cmd.parse_create("~" + test),
                "Invalid class naming"
            )

    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=True
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo"
    )
    def test_parse_create(self, *_):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)

        tests = [
            {
                "input": "Alpha",
                "expected": {
                    "relative_path": True,
                    "class_name": "Alpha",
                    "package": "bravo",
                    "as_main": False,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/",
                    "file": "alpha/bravo/Alpha.java"
                }
            }, {
                "input": "Alpha.Bravo",
                "expected": {
                    "relative_path": True,
                    "class_name": "Bravo",
                    "package": "bravo.Alpha",
                    "as_main": False,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha",
                    "file": "alpha/bravo/Alpha/Bravo.java"
                }
            }, {
                "input": "Alpha.Bravo.Charlie",
                "expected": {
                    "relative_path": True,
                    "class_name": "Charlie",
                    "package": "bravo.Alpha.Bravo",
                    "as_main": False,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha/Bravo",
                    "file": "alpha/bravo/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "Alpha.Bravo.CharlieAsMain",
                "expected": {
                    "relative_path": True,
                    "class_name": "Charlie",
                    "package": "bravo.Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha/Bravo",
                    "file": "alpha/bravo/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "Alpha.Bravo.privateCharlieAsMain",
                "expected": {
                    "relative_path": True,
                    "class_name": "Charlie",
                    "package": "bravo.Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "private",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha/Bravo",
                    "file": "alpha/bravo/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "Alpha.Bravo.abstractCharlieAsMain",
                "expected": {
                    "relative_path": True,
                    "class_name": "Charlie",
                    "package": "bravo.Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "abstract",
                    "directory": "alpha/bravo/Alpha/Bravo",
                    "file": "alpha/bravo/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "Alpha.Bravo.ProtectedFinalCharlieAsMain",
                "expected": {
                    "relative_path": True,
                    "class_name": "Charlie",
                    "package": "bravo.Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "protected",
                    "modifier_keyword": "final",
                    "directory": "alpha/bravo/Alpha/Bravo",
                    "file": "alpha/bravo/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "Alpha.Bravo:Charlie",
                "expected": {
                    "relative_path": True,
                    "class_name": "Bravo",
                    "package": "bravo.Alpha",
                    "as_main": False,
                    "extends": ["Charlie"],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha",
                    "file": "alpha/bravo/Alpha/Bravo.java"
                }
            }, {
                "input": "Alpha.Bravo:Charlie,Delta",
                "expected": {
                    "relative_path": True,
                    "class_name": "Bravo",
                    "package": "bravo.Alpha",
                    "as_main": False,
                    "extends": ["Charlie", "Delta"],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha",
                    "file": "alpha/bravo/Alpha/Bravo.java"
                }
            }, {
                "input": "Alpha.Bravo<Charlie,Delta",
                "expected": {
                    "relative_path": True,
                    "class_name": "Bravo",
                    "package": "bravo.Alpha",
                    "as_main": False,
                    "extends": [],
                    "implements": ["Charlie", "Delta"],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha",
                    "file": "alpha/bravo/Alpha/Bravo.java"
                }
            }, {
                "input": "Alpha.Bravo:Charlie<Delta",
                "expected": {
                    "relative_path": True,
                    "class_name": "Bravo",
                    "package": "bravo.Alpha",
                    "as_main": False,
                    "extends": ["Charlie"],
                    "implements": ["Delta"],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha",
                    "file": "alpha/bravo/Alpha/Bravo.java"
                }
            }, {
                "input": "Alpha.Bravo:Charlie,Delta<Echo,Foxtrot",
                "expected": {
                    "relative_path": True,
                    "class_name": "Bravo",
                    "package": "bravo.Alpha",
                    "as_main": False,
                    "extends": ["Charlie", "Delta"],
                    "implements": ["Echo", "Foxtrot"],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/bravo/Alpha",
                    "file": "alpha/bravo/Alpha/Bravo.java"
                }
            }, {
                "input": "~Alpha",
                "expected": {
                    "relative_path": False,
                    "class_name": "Alpha",
                    "package": "",
                    "as_main": False,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/",
                    "file": "alpha/Alpha.java"
                }
            }, {
                "input": "~Alpha.Bravo",
                "expected": {
                    "relative_path": False,
                    "class_name": "Bravo",
                    "package": "Alpha",
                    "as_main": False,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha",
                    "file": "alpha/Alpha/Bravo.java"
                }
            }, {
                "input": "~Alpha.Bravo.Charlie",
                "expected": {
                    "relative_path": False,
                    "class_name": "Charlie",
                    "package": "Alpha.Bravo",
                    "as_main": False,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha/Bravo",
                    "file": "alpha/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "~Alpha.Bravo.CharlieAsMain",
                "expected": {
                    "relative_path": False,
                    "class_name": "Charlie",
                    "package": "Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha/Bravo",
                    "file": "alpha/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "~Alpha.Bravo.privateCharlieAsMain",
                "expected": {
                    "relative_path": False,
                    "class_name": "Charlie",
                    "package": "Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "private",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha/Bravo",
                    "file": "alpha/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "~Alpha.Bravo.abstractCharlieAsMain",
                "expected": {
                    "relative_path": False,
                    "class_name": "Charlie",
                    "package": "Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "abstract",
                    "directory": "alpha/Alpha/Bravo",
                    "file": "alpha/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "~Alpha.Bravo.ProtectedFinalCharlieAsMain",
                "expected": {
                    "relative_path": False,
                    "class_name": "Charlie",
                    "package": "Alpha.Bravo",
                    "as_main": True,
                    "extends": [],
                    "implements": [],
                    "visibility_keyword": "protected",
                    "modifier_keyword": "final",
                    "directory": "alpha/Alpha/Bravo",
                    "file": "alpha/Alpha/Bravo/Charlie.java"
                }
            }, {
                "input": "~Alpha.Bravo:Charlie",
                "expected": {
                    "relative_path": False,
                    "class_name": "Bravo",
                    "package": "Alpha",
                    "as_main": False,
                    "extends": ["Charlie"],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha",
                    "file": "alpha/Alpha/Bravo.java"
                }
            }, {
                "input": "~Alpha.Bravo:Charlie,Delta",
                "expected": {
                    "relative_path": False,
                    "class_name": "Bravo",
                    "package": "Alpha",
                    "as_main": False,
                    "extends": ["Charlie", "Delta"],
                    "implements": [],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha",
                    "file": "alpha/Alpha/Bravo.java"
                }
            }, {
                "input": "~Alpha.Bravo<Charlie,Delta",
                "expected": {
                    "relative_path": False,
                    "class_name": "Bravo",
                    "package": "Alpha",
                    "as_main": False,
                    "extends": [],
                    "implements": ["Charlie", "Delta"],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha",
                    "file": "alpha/Alpha/Bravo.java"
                }
            }, {
                "input": "~Alpha.Bravo:Charlie<Delta",
                "expected": {
                    "relative_path": False,
                    "class_name": "Bravo",
                    "package": "Alpha",
                    "as_main": False,
                    "extends": ["Charlie"],
                    "implements": ["Delta"],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha",
                    "file": "alpha/Alpha/Bravo.java"
                }
            }, {
                "input": "~Alpha.Bravo:Charlie,Delta<Echo,Foxtrot",
                "expected": {
                    "relative_path": False,
                    "class_name": "Bravo",
                    "package": "Alpha",
                    "as_main": False,
                    "extends": ["Charlie", "Delta"],
                    "implements": ["Echo", "Foxtrot"],
                    "visibility_keyword": "public",
                    "modifier_keyword": "",
                    "directory": "alpha/Alpha",
                    "file": "alpha/Alpha/Bravo.java"
                }
            }
        ]

        for test in tests:
            info = cmd.parse_create(test["input"])
            for key in test["expected"]:
                if key == "package":
                    self.assertEqual(
                        test["expected"][key],
                        info[key].as_class_path()
                    )
                else:
                    self.assertEqual(test["expected"][key], info[key])

    def test_build_prefix(self):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)

        tests = [
            {
                "create_type": "Class",
                "visibility_keyword": "",
                "modifier_keyword": "",
                "as_main": False,
                "expected": "Class"
            }, {
                "create_type": "Interface",
                "visibility_keyword": "public",
                "modifier_keyword": "",
                "as_main": False,
                "expected": "Public interface"
            }, {
                "create_type": "Enumerator",
                "visibility_keyword": "",
                "modifier_keyword": "final",
                "as_main": False,
                "expected": "Final enumerator"
            }, {
                "create_type": "Class",
                "visibility_keyword": "default",
                "modifier_keyword": "abstract",
                "as_main": False,
                "expected": "Default abstract class"
            }, {
                "create_type": "Class",
                "visibility_keyword": "default",
                "modifier_keyword": "abstract",
                "as_main": True,
                "expected": "Default abstract main class"
            }
        ]

        for test in tests:
            cmd.args = {
                "create_type": test["create_type"]
            }
            self.assertEqual(
                cmd.build_prefix(test),
                test["expected"]
            )

    def test_quote_list(self):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)

        self.assertEqual(
            cmd.quote_list([
                "Alpha"
            ]),
            "\"Alpha\""
        )

        self.assertEqual(
            cmd.quote_list([
                "Alpha", "Bravo", "Charlie"
            ]),
            "\"Alpha\", \"Bravo\", \"Charlie\""
        )

    def test_build_additional_text_class(self):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)
        cmd.args = {
            "create_type": "Class"
        }

        self.assertEqual(
            cmd.build_additional_text({
                "extends": ["Alpha", "Bravo"],
                "implements": ["Charlie", "Delta"]
            }),
            ", extends \"Alpha\", \"Bravo\", implements \"Charlie\", \"Delta\" "
            "[Warning! Class can be extent only once]"
        )

        self.assertEqual(
            cmd.build_additional_text({
                "extends": ["Alpha", "Bravo", "Charlie"],
                "implements": ["Delta", "Echo", "Foxtrot"]
            }),
            ", extends \"Alpha\", \"Bravo\" and 1 more classes"
            ", implements \"Delta\", \"Echo\" and 1 more classes "
            "[Warning! Class can be extent only once]"
        )

    def test_build_additional_text_enumerator(self):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)
        cmd.args = {
            "create_type": "Enumerator"
        }

        self.assertEqual(
            cmd.build_additional_text({
                "extends": ["Alpha"],
                "implements": []
            }),
            ", extends \"Alpha\" "
            "[Warning! Enumerator use \"implements\" instead of \"extends\"]"
        )

    def test_build_additional_text_interface(self):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreateCommand(window)
        cmd.args = {
            "create_type": "Interface"
        }

        self.assertEqual(
            cmd.build_additional_text({
                "extends": [],
                "implements": ["Alpha"]
            }),
            ", implements \"Alpha\" "
            "[Warning! Interface use \"extends\" instead of \"implements\"]"
        )


class TestCreatePackage(unittest.TestCase):
    @patch(
        "sublime.Window.folders",
        return_value=[]
    )
    @patch(
        "sublime.Window.active_view",
        return_value=None
    )
    def test_parse_create_invalid_location(self, *_):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreatePackageCommand(window)

        tests = [
            "", "~", "alpha.", ".alpha", ".alpha.",
            "alpha.bravo.", ".alpha.bravo", ".alpha.bravo.", ":charlie",
            "<charlie", ":charlie,delta", "<charlie,delta", "alpha:bravo",
            "alpha<bravo", "alpha:bravo<charlie"
        ]

        for test in tests:
            self.assertEqual(
                cmd.parse_create(test),
                "Cannot specify package location"
            )
            self.assertEqual(
                cmd.parse_create("~" + test),
                "Cannot specify package location"
            )

    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=True
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo"
    )
    def test_parse_create_invalid_name(self, *_):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreatePackageCommand(window)

        tests = [
            "", "~", ":", "<", ":<", "<:", "alpha.", ".alpha", ".alpha.",
            "alpha.bravo.", ".alpha.bravo", ".alpha.bravo.", ":charlie",
            "<charlie", ":charlie,delta", "<charlie,delta", "alpha:bravo",
            "alpha<bravo", "alpha:bravo<charlie"
        ]

        for test in tests:
            self.assertEqual(
                cmd.parse_create(test),
                "Invalid package naming"
            )
            self.assertEqual(
                cmd.parse_create("~" + test),
                "Invalid package naming"
            )

    @patch(
        "Javatar.core.state_property._StateProperty.is_project",
        return_value=True
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_source_folder",
        return_value="alpha"
    )
    @patch(
        "Javatar.core.state_property._StateProperty.get_dir",
        return_value="alpha/bravo"
    )
    def test_parse_create(self, *_):
        window = MagicMock(spec=sublime.Window)
        cmd = JavatarCreatePackageCommand(window)

        tests = [
            {
                "input": "Alpha",
                "expected": {
                    "package": "bravo.Alpha",
                    "directory": "alpha/bravo/Alpha"
                }
            }, {
                "input": "Alpha.Bravo",
                "expected": {
                    "package": "bravo.Alpha.Bravo",
                    "directory": "alpha/bravo/Alpha/Bravo"
                }
            }, {
                "input": "Alpha.Bravo.Charlie",
                "expected": {
                    "package": "bravo.Alpha.Bravo.Charlie",
                    "directory": "alpha/bravo/Alpha/Bravo/Charlie"
                }
            }, {
                "input": "~Alpha",
                "expected": {
                    "package": "Alpha",
                    "directory": "alpha/Alpha"
                }
            }, {
                "input": "~Alpha.Bravo",
                "expected": {
                    "package": "Alpha.Bravo",
                    "directory": "alpha/Alpha/Bravo"
                }
            }, {
                "input": "~Alpha.Bravo.Charlie",
                "expected": {
                    "package": "Alpha.Bravo.Charlie",
                    "directory": "alpha/Alpha/Bravo/Charlie"
                }
            }
        ]

        for test in tests:
            info = cmd.parse_create(test["input"])
            for key in test["expected"]:
                if key == "package":
                    self.assertEqual(
                        test["expected"][key],
                        info[key].as_class_path()
                    )
                else:
                    self.assertEqual(test["expected"][key], info[key])
