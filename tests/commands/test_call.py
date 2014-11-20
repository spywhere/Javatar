import sublime
import unittest
from unittest.mock import patch, MagicMock

from javatar.commands.javatar_call import JavatarCallCommand

MockView = MagicMock(spec=sublime.View)
MockRegion = MagicMock(spec=sublime.Region, a=MagicMock(), b=MagicMock())


class TestCallCommand(unittest.TestCase):
    def setUp(self):
        MockView.reset_mock()
        MockRegion.reset_mock()

    @patch('javatar.commands.javatar_call.is_java', return_value=False)
    @patch('sublime.error_message')
    def test_run_error(self, error_message, is_java):
        # check error conditon
        view = MockView
        JavatarCallCommand(view).run("")
        error_message.assert_called_once_with(
            "Current file is not Java"
        )

    @patch('javatar.commands.javatar_call.is_java', return_value=True)
    @patch('javatar.commands.javatar_call.get_current_package')
    def test_run_package_name(self, get_current_package, is_java):
        selection = MockRegion
        view = MockView
        view.sel.return_value = [selection]
        edit = MagicMock()

        JavatarCallCommand(view).run(edit, "package_name")
        view.insert.assert_called_with(
            edit, selection.a, get_current_package.return_value
        )

    @patch('javatar.commands.javatar_call.is_java', return_value=True)
    @patch('javatar.commands.javatar_call.get_current_package')
    def test_run_subpackage_name(self, get_current_package, is_java):
        selection = MockRegion
        view = MockView
        view.sel.return_value = [selection]
        edit = MagicMock()

        get_current_package.return_value = 'org.google.search'

        JavatarCallCommand(view).run(edit, "subpackage_name")
        view.insert.assert_called_with(
            edit, selection.a, 'search'
        )

    @patch('javatar.commands.javatar_call.is_java', return_value=True)
    @patch('javatar.commands.javatar_call.get_class_name')
    @patch('javatar.commands.javatar_call.get_current_package')
    def test_run_full_class_name(self, get_current_package, get_class_name,
                                 is_java):
        selection = MockRegion
        view = MockView
        view.sel.return_value = [selection]
        edit = MagicMock()

        get_current_package.return_value = 'org.google.search'
        get_class_name.return_value = 'Searcher'

        JavatarCallCommand(view).run(edit, "full_class_name")
        view.insert.assert_called_with(
            edit, selection.a, 'org.google.search.Searcher'
        )

    @patch('javatar.commands.javatar_call.is_java', return_value=True)
    @patch('javatar.commands.javatar_call.get_class_name')
    def test_run_class_name(self, get_class_name, is_java):
        selection = MockRegion
        view = MockView
        view.sel.return_value = [selection]
        edit = MagicMock()

        get_class_name.return_value = 'Searcher'

        JavatarCallCommand(view).run(edit, "class_name")
        view.insert.assert_called_with(
            edit, selection.a, 'Searcher'
        )
