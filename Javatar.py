from .commands import *
from .utils import *


def startup():
    EventHandler.register_handler(on_change, EventHandler.ON_NEW | EventHandler.ON_ACTIVATED | EventHandler.ON_LOAD | EventHandler.ON_POST_SAVE | EventHandler.ON_CLONE)
    EventHandler.register_handler(on_project_stable, EventHandler.ON_CLOSE | EventHandler.ON_NEW | EventHandler.ON_POST_WINDOW_COMMAND)
    start_clock()
    get_action().add_action("javatar", "Startup")
    reset()  # clear data when restart
    read_settings("Javatar.sublime-settings")
    check_news()
    hide_status()
    get_action().add_action("javatar", "Ready")


def plugin_loaded():
    startup()


def on_project_stable(view_or_window=None, command_name=None, args=None):
    save_project_state(repeat=False)


def on_change(view):
    refresh_dependencies()
    hide_status()
