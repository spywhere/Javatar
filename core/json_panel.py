import sublime
import os
from ..core import EventHandler


class JSONPanel:

    """
    A custom buffer for JSON editing which its data will be used on save

    Useful when configure multiple/complex settings
    """

    def __init__(self, window=None, on_done=None, on_cancel=None):
        """
        @param window: window to open panel
        @param on_done: a callback function which will receive Python object
            converted from JSON data when panel is saved
        @param on_cancel: a callback function which will be called when
            panel is closed
        """
        self.window = window
        if self.window is None:
            self.window = sublime.active_window()
        self.on_done = on_done
        self.on_cancel = on_cancel

    def open(self, file_name="jsonpanel_tmp.json", post_remove=True):
        """
        Open panel with specified settings

        @param file_name: file path to store JSON data
        @param post_remove: a boolean specified whether a file path will be
            removed after callback is called or not
        """
        self.post_remove = post_remove
        self.view = self.window.open_file(file_name)
        EventHandler().register_handler(
            self,
            EventHandler().ON_CLOSE | EventHandler().ON_POST_SAVE
        )
        return self.view

    def on_close(self, view):
        """
        Closing event handler
        """
        if self.view.id() == view.id():
            if self.on_cancel is not None:
                self.on_cancel()
            self.cleanup()

    def on_post_save(self, view):
        """
        Saving event handler
        """
        if self.view.id() == view.id():
            if self.on_done is not None:
                self.on_done(sublime.decode_value(self.view.substr(
                    sublime.Region(0, self.view.size()))
                ))
            self.cleanup()

    def cleanup(self):
        """
        Cleanup after callback is called
        """
        EventHandler().unregister_handler(self)
        filepath = self.view.file_name()
        self.window.focus_view(self.view)
        self.window.run_command("close_file")
        if self.post_remove and os.path.exists(filepath):
            os.remove(filepath)
