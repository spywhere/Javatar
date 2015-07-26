import sublime
import sublime_plugin
import os.path
from ...core import Settings, StateProperty
from ...utils import (
    ActionHistory,
    Constant
)


REPORT_TEMPLATE = '''\
## Javatar Report
### System Informations
* Javatar Version: `{javatar_version}`
* Sublime Version: `{sublime_version}`
* Package Path: `{packages_path}`
* Sublime Channel: `{sublime_channel}`
* Is Debug Mode: `{is_debug}`
* Platform: `{platform}`
* As Packages: `{is_package}`
* Package Control: `{package_control}`
* Architecture: `{arch}`
* Javatar's Parent Folder: `{parent_folder}`
* Is Project: `{is_project}`
* Is File: `{is_file}`
* Is Java: `{is_java}`

### Action List
{actions}
'''


class JavatarActionHistoryCommand(sublime_plugin.WindowCommand):

    """
    Command to show an action history
    """

    def get_actions(self, selector):
        selectors = selector.split("|")

        include = selectors.pop(0).split(",")
        exclude = selectors[0].split(",") if selectors else []

        return ActionHistory().get_action(include, exclude)

    def print_action_history(self, selector):
        """
        Show an action history to user using specified selector

        @param selector: a action selector
        """
        selector = selector or ""
        actions = self.get_actions(selector)

        actionText = "\n".join(
            "{}. {}".format(i, action)
            for i, action in enumerate(actions, 1)
        )

        report = REPORT_TEMPLATE.format_map({
            "javatar_version": Constant.get_version(),
            "is_package": os.path.exists(os.path.join(
                sublime.installed_packages_path(), "Javatar.sublime-package")
            ),
            "parent_folder": __name__.split('.')[0],
            "sublime_version": sublime.version(),
            "sublime_channel": sublime.channel(),
            "is_debug": Settings().get("debug_mode"),
            "package_control": (os.path.exists(
                os.path.join(sublime.packages_path(), "Package Control")
            ) or os.path.exists(os.path.join(
                sublime.installed_packages_path(),
                "Package Control.sublime-package"
            ))),
            "is_project": StateProperty().is_project(),
            "is_file": StateProperty().is_file(),
            "is_java": StateProperty().is_java(),
            "packages_path": sublime.packages_path(),
            "platform": sublime.platform(),
            "arch": sublime.arch(),
            "actions": actionText,
        })

        view = self.window.new_file()
        view.set_name("Javatar Action History Report")
        view.set_scratch(True)
        view.run_command("javatar_utils", {
            "util_type": "add",
            "text": report,
            "dest": "Action History"
        })
        view.run_command("javatar_utils", {"util_type": "set_read_only"})

    def run(self, selector=None):
        """
        Create a specified Java file

        @param create_type: a snippet type to create
        """
        if not Settings().get("enable_action_history"):
            sublime.message_dialog(
                "Actions History is disabled. Please enable them first."
            )
            return

        if selector is None:
            self.window.show_input_panel(
                "Selector: ",
                "",
                self.print_action_history,
                None,
                None
            )
            return
        self.print_action_history("")
