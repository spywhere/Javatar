import sublime
from .javatar_actions import *
from .javatar_updater import *

# YY.MM.DD.HH.MM
VERSION = "14.04.13.17.03b"
UPDATEFOR = "dev"
NEWSID = 10
NEWS = " - Javatar now supported create your own packages via Packages Manager... > Package Tools...\n - Javatar will now collected some usage and send to the server to help improve the package. You can disable this settings by set \"send_stats_and_usages\" to \"false\""

def getVersion():
	return VERSION


def getUsageData():
	data = {}
	from .javatar_utils import getSettings, setSettings, getPath
	data["JavatarVersion"] = getVersion()
	data["JavatarChannel"] = str.lower(getSettings("package_channel"))
	data["JavatarDebugMode"] = str(getSettings("debug_mode"))
	data["JavatarAsPackage"] = str(getPath("exist", getPath("join", sublime.installed_packages_path(), "Javatar.sublime-package")))
	data["JavatarNews"] = str(getSettings("message_id"))
	data["JavatarActionHistory"] = str(getSettings("enable_actions_history"))
	data["JavatarSendUsage"] = str(getSettings("send_stats_and_usages"))
	data["SublimeVersion"] = str(sublime.version())
	data["Platform"] = sublime.platform()
	return data


def checkNews():
	getAction().addAction("javatar.util.news", "Check news")
	from .javatar_utils import getSettings, setSettings, isStable
	if getSettings("message_id") < NEWSID:
		if getSettings("message_id") != -1:
			if isStable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
				setSettings("message_id", NEWSID)
				getAction().addAction("javatar.util.news", "Show stable news")
			elif not isStable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
				getAction().addAction("javatar.util.news", "Show dev news")
				setSettings("message_id", NEWSID)
			sendUsages(getUsageData())
		elif getSettings("javatar_gp") & 0x1 == 0:
			sendUsages(getUsageData(), True)
