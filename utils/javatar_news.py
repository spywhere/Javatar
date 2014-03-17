import sublime
from .javatar_actions import *

# YY.MM.DD.HH.MM
VERSION = "14.03.17.07.47b"
UPDATEFOR = "dev"
NEWSID = 8
NEWS = " - Many additional packages now available through Help and Support... > Download Packages\n - HUGE startup time improvements"

def getVersion():
	return VERSION

def checkNews():
	getAction().addAction("javatar.util.news", "Check news")
	from .javatar_utils import getSettings, setSettings, isStable
	if getSettings("message_id") < NEWSID and getSettings("message_id") != -1:
		if isStable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
			sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
			setSettings("message_id", NEWSID)
			getAction().addAction("javatar.util.news", "Show stable news")
		elif not isStable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
			sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
			getAction().addAction("javatar.util.news", "Show dev news")
			setSettings("message_id", NEWSID)
