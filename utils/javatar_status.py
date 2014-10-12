import sublime
from .javatar_utils import *


STATUS_NAME = "Javatar"
STATUS = None
TAB_NOTIFICATION = None


class JavatarTabNotification():
	running = False
	views = []

	def notify(self, view, times=None):
		self.views.append([view, view.name(), times])
		if not self.running:
			sublime.set_timeout(lambda: self.run(), 10)
			self.running = True

	def on_activated(self, view):
		for view_info in self.views:
			if view_info[0].id() == view.id():
				view_info[0].set_name(view_info[1])
				self.views.remove(view_info)
				break

	def run(self, i=0):
		index = 0
		for view_info in self.views:
			if view_info[2] is None or view_info[2] > 0:
				view_info[0].set_name(view_info[1]+("!"*i))
				if view_info[2] is not None:
					self.views[index][2] -= 1
			else:
				view_info[0].set_name(view_info[1]+"!")
			index += 1
		self.running = len(self.views) > 0
		if self.running:
			sublime.set_timeout(lambda: self.run((i+1)%2), 500)

class JavatarStatus():
	delay = 0
	permtext = ""
	running = False

	def set_status(self, text, delay=None, require_java=False):
		if delay is None:
			self.delay = get_settings("status_delay")
		else:
			if delay < 0:
				self.permtext = text
			else:
				self.delay = delay
		from .javatar_validator import is_java
		if not is_java() and require_java:
			return
		view = sublime.active_window().active_view()
		view.set_status(STATUS_NAME, text)

		if not self.running:
			sublime.set_timeout(lambda: self.run(), 10)
			self.running = True

	def hide_status(self, clear=False):
		if clear:
			self.permtext = ""
		view = sublime.active_window().active_view()
		if view is not None:
			from .javatar_validator import is_java
			if is_ready() and is_java() and get_settings("show_package_path"):
				if self.permtext == "":
					view.set_status(STATUS_NAME, "Package: " + to_readable_package(get_current_package(), True))
				else:
					view.set_status(STATUS_NAME, self.permtext)
			elif self.permtext == "":
				view.erase_status(STATUS_NAME)
		self.running = False

	def run(self):
		self.delay -= 100
		if self.delay <= 0:
			self.hide_status()
			self.running = False
		if self.running:
			sublime.set_timeout(lambda: self.run(), 100)

def get_status():
	global STATUS
	if STATUS is None:
		STATUS = JavatarStatus()
	return STATUS

def get_tab_notification():
	global TAB_NOTIFICATION
	if TAB_NOTIFICATION is None:
		TAB_NOTIFICATION = JavatarTabNotification()
	return TAB_NOTIFICATION
