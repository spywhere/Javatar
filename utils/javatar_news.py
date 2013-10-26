import sublime
from .javatar_actions import *


UPDATEFOR = "dev"
NEWSID = 2
NEWS = " - Fix a notification system (this message may appear on stable channel)\n - Added Help and Support section for issue support\n - Organize Imports: Now use Sublime system instead of reinventing the wheel\n - Actions History: Tracking of your Javatar actions\n - Due to working with a new Organize Imports system, most RegEx in settings file will be removed after this feature is completed\n\nPlease check out new menu in Javatar: Browse Commands"


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