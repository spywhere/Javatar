from .utils import *
from .commands import *
from .completions import *


def plugin_loaded():
	getAction().addAction("javatar", "Startup")
	reset() # clear data when restart
	readSettings("Javatar.sublime-settings")
	checkNews()
	hideStatus()
	getAction().addAction("javatar", "Ready")


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
