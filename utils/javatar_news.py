import sublime
from .javatar_actions import *
from .javatar_updater import *

# YY.MM.DD.HH.MM
VERSION = "14.04.25.16.36b"
UPDATEFOR = "all"
NEWSID = 14
NEWS = " - Run Main Class feature, now available on Stable Channel\n - Fix internal shell did not work on Windows, finally\n - Multi-thread build system now support\n - Fix Run Main Class error when run on an empty window\n\nSee README for more info and also a new screenshot"


def getVersion():
	return VERSION


def getUsageData():
	data = {}
	from .javatar_utils import getSettings, setSettings, getPath
	data["SchemaVersion"] = getSchemaVersion()
	data["JavatarVersion"] = getVersion()
	data["JavatarChannel"] = str.lower(getSettings("package_channel"))
	data["JavatarDebugMode"] = str.lower(str(getSettings("debug_mode")))
	data["JavatarAsPackage"] = str.lower(str(getPath("exist", getPath("join", sublime.installed_packages_path(), "Javatar.sublime-package"))))
	data["JavatarNews"] = str(getSettings("message_id"))
	data["JavatarActionHistory"] = str.lower(str(getSettings("enable_actions_history")))
	data["JavatarSendUsage"] = str.lower(str(getSettings("send_stats_and_usages")))
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
				getAction().addAction("javatar.util.news", "Show stable news")
			elif not isStable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
				getAction().addAction("javatar.util.news", "Show dev news")
			sendUsages(getUsageData())
			setSettings("message_id", NEWSID)
		elif getSettings("javatar_gp") & 0x1 == 0:
			sendUsages(getUsageData(), True)
