from ..core import (
    DependencyManager,
    EventHandler,
    ProjectRestoration,
    StateProperty
)
from Javatar.api import *


class JavatarProjectRestoration(JavatarPlugin):
    def on_load(self):
        EventHandler().register_handler(
            lambda view=None:
            self.on_change(self, view),
            (
                EventHandler().ON_NEW |
                EventHandler().ON_ACTIVATED |
                EventHandler().ON_LOAD |
                EventHandler().ON_POST_SAVE |
                EventHandler().ON_CLONE
            )
        )
        EventHandler().register_handler(
            lambda view_or_window=None, command_name=None, args=None:
            self.on_project_stable(self, view_or_window, command_name, args),
            (
                EventHandler().ON_CLOSE |
                EventHandler().ON_NEW |
                EventHandler().ON_POST_WINDOW_COMMAND
            )
        )

    def on_project_stable(self, view_or_window=None, command_name=None,
                          args=None):
        ProjectRestoration().save_state()

    def on_change(self, view):
        DependencyManager().refresh_dependencies()
        StateProperty().refresh_library_paths()
        StateProperty().refresh_source_folders()
