import sublime
from .javatar_actions import *

# YY.MM.DD.HH.MM
VERSION = "14.03.14.19.52b"
UPDATEFOR = "dev"
NEWSID = 7
NEWS = " - Organize Imports now worked on new, unsave file\n - Organize Imports should leave a blank space properly\n - Class detection in Organize Imports improvements"

def getVersion():
	return VERSION

def checkNews():
	getAction().addAction("javatar.util.news", "Check news")
	from .javatar_utils import getSettings, setSettings, isStable
	if getSettings("message_id") < NEWSID and getSettings("message_id") != -1:
		if isStable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
			sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
			setSettings("message_id", NEWSID)
		elif not isStable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
			sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
			setSettings("message_id", NEWSID)
