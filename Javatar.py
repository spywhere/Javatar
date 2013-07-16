import sublime
from Javatar.utils import *
from Javatar.commands import *


def plugin_loaded():
    config = sublime.load_settings("Javatar.sublime-settings")
    readSettings(config)
