import sublime
from .javatar_actions import *
from .javatar_updater import *


# YY.MM.DD.HH.MM
VERSION = "14.05.02.01.02b"
UPDATEFOR = "all"
NEWSID = 15
NEWS = " - JDK Settings, now you can select which JDK you want to use. And also no more PATH settings now :D\n - Build and Run with dependencies\n\nJavatar has grow so much since the beginning, the manual is also bigger, so that Javatar has changed the README file to JavatarDoc that hosted on readthedocs.org instead. A link to JavatarDoc is located inside README file."


def get_version():
	return VERSION


def get_usage_data():
	data = {}
	from .javatar_utils import get_settings, set_settings, get_path
	data["SchemaVersion"] = get_schema_version()
	data["JavatarVersion"] = get_version()
	data["JavatarChannel"] = str.lower(get_settings("package_channel"))
	data["JavatarDebugMode"] = str.lower(str(get_settings("debug_mode")))
	data["JavatarAsPackage"] = str.lower(str(get_path("exist", get_path("join", sublime.installed_packages_path(), "Javatar.sublime-package"))))
	data["JavatarNews"] = str(get_settings("message_id"))
	data["JavatarActionHistory"] = str.lower(str(get_settings("enable_actions_history")))
	data["JavatarSendUsage"] = str.lower(str(get_settings("send_stats_and_usages")))
	data["SublimeVersion"] = str(sublime.version())
	data["Platform"] = sublime.platform()
	return data


def check_news():
	get_action().add_action("javatar.util.news", "Check news")
	from .javatar_utils import get_settings, set_settings, is_stable
	if get_settings("message_id") < NEWSID:
		if get_settings("message_id") != -1:
			if is_stable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
				get_action().add_action("javatar.util.news", "Show stable news")
			elif not is_stable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
				get_action().add_action("javatar.util.news", "Show dev news")
			send_usages(get_usage_data())
			set_settings("message_id", NEWSID)
		elif get_settings("javatar_gp") & 0x1 == 0:
			send_usages(get_usage_data(), True)
