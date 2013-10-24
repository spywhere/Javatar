import sublime


UPDATEFOR = "all"
NEWSID = 1
NEWS = " - Now using QuickMenu for easier command browsing\n - Package update status: Showing you the latest important news about a new build\n - Package channel: Dev or Stable (so there will be more updates but not affect any part of stable channel)\n - Due to working with Organize Imports feature, please check your RegEx settings since it has been added/changed to support upcoming feature\n\nPlease check out new settings in settings file"


def checkNews():
	from .javatar_utils import getSettings, setSettings, isStable
	if getSettings("message_id") != 1 and getSettings("message_id") != -1:
		if isStable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
			sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
		elif UPDATEFOR == "dev" or UPDATEFOR == "all":
			sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
		setSettings("message_id", NEWSID)