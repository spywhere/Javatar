from ..core import PluginManager


class JavatarMetaPlugin(type):
    def __init__(cls, name, bases, attrs):
        if name in ["JavatarPlugin"]:
            return
        PluginManager().register_plugin(cls)

    @property
    def name(cls):
        return cls.__name__

    @property
    def description(cls):
        return "A Javatar extension plugin"


class JavatarPlugin(metaclass=JavatarMetaPlugin):
    def on_setup_menu(self, menu):
        pass

    def on_load(self):
        pass
