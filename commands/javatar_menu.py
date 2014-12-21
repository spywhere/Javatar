import sublime
import sublime_plugin
from ..QuickMenu.QuickMenu import QuickMenu
from ..utils.javatar_actions import add_action


class JavatarCommand(sublime_plugin.WindowCommand):
    qm = None

    @property
    def menuStable(self):
        try:
            return self._menuStable
        except AttributeError:
            self._menuStable = sublime.decode_value(sublime.load_resource(
                'Packages/Javatar/commands/menu.json'
            ))

        return self._menuStable

    def run(self, menu=None, action=None, replaceMenu=None):
        if self.qm is None:
            from ..utils import get_snippet_list, is_stable, is_debug
            self.qm = QuickMenu(self.menuStable)
            # Create a menu for development channel
            if not is_stable():
                self.qm.addItems("main", [["Development Section...", "All testing features"]], [{"name": "dev"}])

            # Generate action for Create menu
            actions = []
            for snippet in get_snippet_list():
                actions += [{"command": "javatar_create", "args": {"create_type": snippet[0]}}]
            self.qm.addItems("creates", get_snippet_list(), actions)
            self.qm.setSelectedIndex("creates", 3 if len(actions) > 0 else 2)

            # Always add Help and Support at the end
            self.qm.addItems("main", [["Help and Support...", "Utilities for Help and Support on Javatar"]], [{"name": "help"}])

            # Quick reload menu
            if is_debug():
                self.qm.insertItem("main", 0, ["Reload Javatar", "Reload Javatar modules (debug only)"], {"command": "javatar_util", "args": {"util_type": "reload"}})
            from ..utils.javatar_news import get_version
            self.qm.addItems("help", [["Javatar", "v" + get_version()]], [{}])
        if replaceMenu is not None:
            self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
            return
        self.qm.show(self.window, self.select, menu, action)

    def select(self, info):
        if info["index"] < 0:
            add_action(
                "javatar.command.menu.select",
                "Exit menu [from_sublime={}]".format(
                    info["from_sublime"]
                )
            )
        else:
            add_action(
                "javatar.command.menu.select",
                "Select item {} [from_sublime={}]".format(
                    info["items"][info["index"]],
                    info["from_sublime"]
                )
            )
