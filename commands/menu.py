import sublime
import sublime_plugin
from ..QuickMenu.QuickMenu import QuickMenu
from ..core import PluginManager
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
            return PluginManager().get_plugin_menu(self._main_menu)
        except AttributeError:
            self._main_menu = sublime.decode_value(sublime.load_resource(
                "Packages/Javatar/menu/MainMenu.json"
            ))
        return self.main_menu

    def run(self, menu=None, action=None, replaceMenu=None):
        """
        Show menu to user, if ready
        """
        if not Constant.ready():
            if not replaceMenu:
                if self.ready_retry > 2:
                    sublime.message_dialog(
                        "Javatar is starting up... " +
                        "Please wait a few seconds and try again."
                    )
                else:
                    sublime.status_message(
                        "Javatar is starting up... " +
                        "Please wait a few seconds and try again..."
                    )
                self.ready_retry += 1
            return
        if self.qm is None:
            self.qm = QuickMenu(self.main_menu)
        if replaceMenu is not None:
            self._main_menu[replaceMenu["name"]] = replaceMenu["menu"]
            return
        else:
            PluginManager().on_presetup_menu()
            for key, menu in self.main_menu.items():
                self.qm.setMenu(key, menu)
        self.qm.show(self.window, self.select, menu, action)

    def select(self, info):
        """
        Logging method for menu
        """
        if info["index"] < 0:
            ActionHistory().add_action(
                "javatar.commands.menu.select",
                "Exit menu [from_sublime={from_sublime}]".format_map(info)
            )
        else:
            ActionHistory().add_action(
                "javatar.commands.menu.select",
                "Select item {index} [from_sublime={from_sublime}]".format_map(
                    {
                        "index": info["items"][info["index"]],
                        "from_sublime": info["from_sublime"]
                    }
                )
            )
