import sublime
from .javatar_actions import *

# YY.MM.DD.HH.MM
VERSION = "14.04.12.00.13b"
UPDATEFOR = "all"
NEWSID = 9
NEWS = " - Most of Javatar commands now available through Command Palette\n - Javatar now contains no Javatar packages as default (but it will install necessary packages on startup). See more details in README file\n - Additional packages now moved to a new menu, Packages Manager\n - 3 additional packages now available through Packages Manager... > Install Packages...\n - Most of this update is focus on Javatar packages."

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
