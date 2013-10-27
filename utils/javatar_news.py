import sublime
from .javatar_actions import *


VERSION = "13.10.27.8.25b"
UPDATEFOR = "dev"
NEWSID = 3
NEWS = " - Organize Imports: Now available to test!\n - Improved Class Correction\n - Many RegEx has been removed, please check it out if you are using it\n\nPlease try it out in Development Section"


def getVersion():
    return VERSION

def checkNews():
    getAction().addAction("javatar.util.news", "Check news")
    from .javatar_utils import getSettings, setSettings, isStable
    if getSettings("message_id") != NEWSID and getSettings("message_id") != -1:
        if isStable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
            sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
            setSettings("message_id", NEWSID)
        elif not isStable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
            sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
            setSettings("message_id", NEWSID)