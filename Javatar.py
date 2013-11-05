import sublime
import sublime_plugin
from .commands import *
from .completions import *
from .utils import *


def startup():
	getAction().addAction("javatar", "Startup")
	reset() # clear data when restart
	readSettings("Javatar.sublime-settings")
	checkNews()
	hideStatus()
	getAction().addAction("javatar", "Ready")


def plugin_loaded():
	sublime.set_timeout(startup, 50)


class EventListener(sublime_plugin.EventListener):
	def on_new(self, view):
		hideStatus()

	def on_activated(self, view):
		sublime.set_timeout(hideStatus, 50)

	def on_load(self, view):
		hideStatus()

	def on_post_save(self, view):
		hideStatus()

	def on_clone(self, view):
		hideStatus()
