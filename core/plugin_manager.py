import copy


class PluginMenu:
    def __init__(self, menu):
        self.menu = copy.deepcopy(menu)

    def add_menu(self, menu_name, menu):
        if menu_name in self.menu:
            return
        self.menu[menu_name] = menu

    def add_item(self, menu_name, item, action, index=None):
        if menu_name not in self.menu:
            self.menu[menu_name] = {
                "items": [],
                "actions": []
            }
        if index is not None and isinstance(index, int):
            size = len(self.menu[menu_name]["items"])
            if index < -size or index >= size:
                return
            self.menu[menu_name]["items"].insert(index, item)
            self.menu[menu_name]["actions"].insert(index, action)
        elif index is None:
            self.menu[menu_name]["items"].append(item)
            self.menu[menu_name]["actions"].append(action)

    def add_items(self, menu_name, items, actions):
        if not isinstance(items, list) and not isinstance(items, tuple):
            return
        elif not isinstance(actions, list) and not isinstance(actions, tuple):
            return
        elif len(items) != len(actions):
            return
        for index in range(len(items)):
            self.add_item(menu_name, items[index], actions[index])

    def set_selected_index(self, menu_name, index):
        if menu_name not in self.menu:
            return
        self.menu[menu_name]["selected_index"] = index

    def remove_item(self, menu_name, item):
        if menu_name not in self.menu:
            return
        if not isinstance(item, int):
            try:
                item = self.menu[menu_name]["items"].index(item)
            except:
                return
        size = len(self.menu[menu_name]["items"])
        if item < -size or item >= size:
            return
        del self.menu[menu_name]["items"][item]
        del self.menu[menu_name]["actions"][item]

    def replace_item(self, menu_name, item, action):
        if menu_name not in self.menu:
            return
        if not isinstance(item, int):
            try:
                item = self.menu[menu_name]["items"].index(item)
            except:
                return
        size = len(self.menu[menu_name]["items"])
        if item < -size or item >= size:
            return
        self.menu[menu_name]["actions"][item] = action

    def get_menu(self):
        return self.menu


class _PluginManager:
    plugins = []

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def register_plugin(self, plugin):
        from ..utils import Constant
        if plugin.debug_only(plugin) and not Constant.is_debug():
            return
        self.plugins.append(plugin)

    def load_plugins(self):
        from .action_history import ActionHistory
        from .logger import Logger
        ActionHistory().add_action(
            "javatar.core.plugin_manager.load_plugins", "Load plugins"
        )
        for plugin in self.plugins:
            Logger().info(
                "Javatar extension plugin \"%s\" has been loaded" % (
                    plugin.name
                )
            )
            plugin.on_load(plugin)

    def on_presetup_menu(self):
        for plugin in self.plugins:
            plugin.on_presetup_menu(plugin)

    def get_plugin_menu(self, menu):
        plugin_menu = PluginMenu(menu)
        for plugin in self.plugins:
            plugin.on_setup_menu(plugin, plugin_menu)

        return plugin_menu.get_menu()


def PluginManager():
    return _PluginManager.instance()
