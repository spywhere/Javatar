import os

import sublime
from .javatar_event_handler import EventHandler


class JSONPanel():
    def __init__(self, window=None, on_done=None, on_cancel=None):
        self.window = window
        if self.window is None:
            self.window = sublime.active_window()
        self.on_done = on_done
        self.on_cancel = on_cancel

    def open(self, file_name="jsonpanel_tmp.json", post_remove=True):
        self.post_remove = post_remove
        self.view = self.window.open_file(file_name)
        EventHandler.register_handler(self, EventHandler.ON_CLOSE | EventHandler.ON_POST_SAVE)
        return self.view

    def on_close(self, view):
        if self.view.id() == view.id() and self.on_cancel is not None:
            self.on_cancel()
            self.cleanup()

    def on_post_save(self, view):
        if self.view.id() == view.id() and self.on_done is not None:
            self.on_done(sublime.decode_value(self.view.substr(sublime.Region(0, self.view.size()))))
            self.cleanup()

    def cleanup(self):
        EventHandler.unregister_handler(self)
        filepath = self.view.file_name()
        self.window.focus_view(self.view)
        self.window.run_command("close_file")
        if self.post_remove and os.path.exists(filepath):
            os.remove(filepath)
