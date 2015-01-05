import sublime
import sublime_plugin
from ..QuickMenu.QuickMenu import QuickMenu
from ..utils import (
    ActionHistory,
    Constant
)


class JavatarCommand(sublime_plugin.WindowCommand):

    """
    Command to show menu which use to run another command
    """

    qm = None
    ready_retry = 0

    @property
    def main_menu(self):
        """
        Returns Python object represents a menu
        """
        try:
            return self._main_menu
        except AttributeError:
            self._main_menu = sublime.decode_value(sublime.load_resource(
                "Packages/Javatar/menu/MainMenu.json"
            ))
        return self._main_menu

    def run(self, menu=None, action=None, replaceMenu=None):
        """
        Show menu to user, if ready
        """
        if not Constant.ready():
            if self.ready_retry > 3:
                sublime.message_dialog("Javatar is starting up... Please wait a few seconds and try again.")
            else:
                sublime.status_message("Javatar is starting up... Please wait a few seconds and try again...")
            self.ready_retry += 1
            return
        if self.qm is None:
            # from ..utils import get_snippet_list
            self.qm = QuickMenu(self.main_menu)
            # Create a menu for development channel
            if Constant.is_debug():
                self.qm.addItems("main", [["Development Section...", "All testing tools"]], [{"name": "dev"}])

            # Generate action for Create menu
            # actions = []
            # for snippet in get_snippet_list():
            #     actions += [{"command": "javatar_create", "args": {"create_type": snippet[0]}}]
            # self.qm.addItems("creates", get_snippet_list(), actions)
            # self.qm.setSelectedIndex("creates", 3 if len(actions) > 0 else 2)

            # Always add Help and Support at the end
            self.qm.addItems("main", [["Help and Support...", "Utilities for Help and Support on Javatar"]], [{"name": "help"}])

            # Quick reload menu
            if Constant.is_debug():
                self.qm.insertItem("main", 0, ["Reload Javatar", "Reload Javatar modules (debug only)"], {"command": "javatar_utils", "args": {"util_type": "reload"}})
            self.qm.addItems("help", [["Javatar", "v" + Constant.get_version()]], [{}])
        if replaceMenu is not None:
            self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
            return
        self.qm.show(self.window, self.select, menu, action)

    def select(self, info):
        if info["index"] < 0:
            ActionHistory.add_action(
                "javatar.commands.menu.select",
                "Exit menu [from_sublime={from_sublime}]".format_map(info)
            )
        else:
            ActionHistory.add_action(
                "javatar.commands.menu.select",
                "Select item {index} [from_sublime={from_sublime}]".format_map(
                    {
                        "index": info["items"][info["index"]],
                        "from_sublime": info["from_sublime"]
                    }
                )
            )
