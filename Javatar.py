import sublime
import sublime_plugin
from .commands import *
from .completions import *
from .utils import *


def startup():
	get_action().add_action("javatar", "Startup")
	reset() # clear data when restart
	read_settings("Javatar.sublime-settings")
	check_news()
	hide_status()
	get_action().add_action("javatar", "Ready")


def plugin_loaded():
	startup()


class EventListener(sublime_plugin.EventListener):
	def on_new(self, view):
		hide_status()

	def on_activated(self, view):
		hide_status()

	def on_load(self, view):
		hide_status()

	def on_post_save(self, view):
		hide_status()

	def on_clone(self, view):
		hide_status()
