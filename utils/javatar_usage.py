import sublime
import threading
import urllib
import hashlib
from .javatar_collections import *
from .javatar_thread import *
from .javatar_utils import *


USAGE_VERSION = "0.1"
# If you are going to visit the site, sorry for the crap design...
PACKAGES_STATS = "http://digitalparticle.in.th/javatar/"


def get_usage_version():
	return USAGE_VERSION


def get_usage_data():
	data = {}
	from .javatar_news import get_version
	from .javatar_utils import get_settings, set_settings, get_path
	data["SchemaVersion"] = get_usage_version()
	data["JavatarVersion"] = get_version()
	data["JavatarChannel"] = str.lower(get_settings("package_channel"))
	data["JavatarDebugMode"] = str.lower(str(get_settings("debug_mode")))
	data["JavatarAsPackage"] = str.lower(str(get_path("exist", get_path("join", sublime.installed_packages_path(), "Javatar.sublime-package"))))
	data["JavatarStartupTime"] = "{0:.2f}s".format(get_startup_time())
	data["JavatarNews"] = str(get_settings("message_id"))
	data["JavatarActionHistory"] = str.lower(str(get_settings("enable_actions_history")))
	data["JavatarSendUsage"] = str.lower(str(get_settings("send_stats_and_usages")))
	data["SublimeVersion"] = str(sublime.version())
	data["Platform"] = sublime.platform()
	return data


def send_usages(params={}, lasttime=False):
	if get_settings("send_stats_and_usages"):
		params["usage"] = "true"
		thread = JavatarPackageUsageThread(params, lasttime)
		thread.start()
		SilentThreadProgress(thread, send_usage_complete)


def send_usage_complete(thread):
	if thread.result:
		if thread.lasttime:
			if is_debug():
				print("Javatar usage data sent as last time: " + thread.data)
			set_settings("javatar_gp", get_settings("javatar_gp")|0x1)
		else:
			if is_debug():
				print("Javatar usage data sent: " + thread.data)
			set_settings("javatar_gp", get_settings("javatar_gp")&(~0x1))


class JavatarPackageUsageThread(threading.Thread):
	def __init__(self, params={}, lasttime=False):
		self.lasttime = lasttime
		self.params = params
		threading.Thread.__init__(self)

	def run(self):
		try:
			urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()))
			url = PACKAGES_STATS+"?"+urllib.parse.urlencode(self.params)
			data = urllib.request.urlopen(url).read()
			self.data = str(data)
			self.datahash = hashlib.sha256(self.data.encode("utf-8")).hexdigest()
			self.result = True
		except Exception as e:
			if is_debug():
				print("Javatar Usage: " + str(e))
			self.result = False
