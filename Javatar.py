from Javatar.utils import *
from Javatar.commands import *


def plugin_loaded():
    reset() # clear data when restart
    readSettings("Javatar.sublime-settings")
    checkNews()
    hideStatus()


class EventListener(sublime_plugin.EventListener):
    def on_new(self, view):
        hideStatus()

    def on_activated(self, view):
        hideStatus()

    def on_load(self, view):
        hideStatus()

    def on_post_save(self, view):
        hideStatus()

    def on_clone(self, view):
        hideStatus()
