import sublime
from .javatar_actions import *

VERSION = "14.03.12.21.10b"
UPDATEFOR = "all"
NEWSID = 6
NEWS = "Stable Channel\n - New key bindings has been added. Please check README file for more infomations.\n - Startup time improvement for Stable channel\n - Default imports has been removed from settings. If you want to import your own pacakge, use Javatar Package instead.\n\nDevelopment Channel\n - Organize Imports now use all references from Javatar Packages.\n - Organize Imports improvements\n - Javatar Imports has been removed from Javatar. If you are using it, please convert using Convert Imports in Development Section menu.\n - Manual package input box will append class name automatically when imported."

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
