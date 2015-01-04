from .commands import *
from .utils import (
    ActionHistory,
    Constant,
    EventHandler,
    Settings
)


def startup():
    EventHandler.register_handler(on_change, EventHandler.ON_NEW | EventHandler.ON_ACTIVATED | EventHandler.ON_LOAD | EventHandler.ON_POST_SAVE | EventHandler.ON_CLONE)
    EventHandler.register_handler(on_project_stable, EventHandler.ON_CLOSE | EventHandler.ON_NEW | EventHandler.ON_POST_WINDOW_COMMAND)
    Constant.reset()
    ActionHistory.add_action("javatar", "Startup")
    Settings.read_settings()

    # hide_status()

    ActionHistory.add_action("javatar", "Ready")


def plugin_loaded():
    startup()


def on_project_stable(view_or_window=None, command_name=None, args=None):
    pass
    # save_project_state(repeat=False)


def on_change(view):
    pass
    # refresh_dependencies()
    # hide_status()
