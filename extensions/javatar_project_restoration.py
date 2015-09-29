from ..core import (
    EventHandler,
    ProjectRestoration
)
from Javatar.api import *


class JavatarProjectRestoration(JavatarPlugin):
    def on_load(self):
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
