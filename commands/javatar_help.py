from os.path import join, exists

import sublime
import sublime_plugin
from ..utils import (
    get_javatar_parent,
    get_settings,
    get_version,
    is_project,
    is_file,
    is_java,
    get_action
)


REPORT_TEMPLATE = '''\
## Javatar Report
### System Informations
* Javatar Version: `{javatar_version}`
* Sublime Version: `{sublime_version}`
* Package Path: `{packages_path}`
* Javatar Channel: `{javatar_channel}`
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


class JavatarHelpCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.action = ""
        super().__init__(window)

    def run(self, selector=None, action=""):
        if self.action != "":
            action = self.action
            self.action = ""
        if action == "actions_history":
            self.actions_history(selector, action)

    def actions_history(self, selector, action):
        if not get_settings("enable_actions_history"):
            sublime.message_dialog("Actions History is disabled. Please enable them first.")
            return

        self.action = action
        if selector is None:
            self.window.show_input_panel("Selector: ", "", self.run, "", "")
            return

        selectors = selector.split("|")
        if len(selectors) > 1:
            include = selectors[0].split(",")
            exclude = selectors[1].split(",")
        else:
            include = selectors[0].split(",")
            exclude = []

        actions = get_action().get_action(include, exclude)
        actionText = '\n'.join(
            '{}. {}'.format(i, action)
            for i, action in enumerate(actions, 1)
        )

        report = REPORT_TEMPLATE.format_map({
            "javatar_version": get_version(),
            "javatar_channel": str.lower(get_settings("package_channel")),
            "is_package": exists(join(sublime.installed_packages_path(), "Javatar.sublime-package")),
            "parent_folder": get_javatar_parent(),
            "sublime_version": sublime.version(),
            "sublime_channel": sublime.channel(),
            "is_debug": get_settings("debug_mode"),
            "package_control": exists(join(sublime.packages_path(), "Package Control")) or exists(join(sublime.installed_packages_path(), "Package Control.sublime-package")),
            "is_project": is_project(),
            "is_file": is_file(),
            "is_java": is_java(),
            "packages_path": sublime.packages_path(),
            "platform": sublime.platform(),
            "arch": sublime.arch(),
            "actions": actionText,
        })

        view = self.window.new_file()
        view.set_name("Javatar Actions History Report")
        view.set_scratch(True)
        view.run_command("javatar_util", {"util_type": "add", "text": report, "dest": "Actions History"})
        view.run_command("javatar_util", {"util_type": "set_read_only"})
