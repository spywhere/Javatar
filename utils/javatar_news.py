import sublime
from .javatar_actions import *


VERSION = "13.10.30.4.4b"
UPDATEFOR = "dev"
NEWSID = 5
NEWS = "- Full Java SE7 Imports added (Java SE8 should coming soon...)\n- Javatar Imports improvements, now types separated and also backward compatible\n- QuickMenu updated\n- Debug command added (Javatar Util)\n- Typo fixed\n\nTry it out in Development Section"

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
