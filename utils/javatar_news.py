import sublime
from .javatar_actions import *
from .javatar_updater import *
from .javatar_usage import send_usages, get_usage_data


# YY.MM.DD.HH.MM
VERSION = "14.05.18.03.31b"
UPDATEFOR = "all"
NEWSID = 16
NEWS = " - Javatar now nest project settings inside \"Javatar\" key\n - Fix path not working properly in some cases\n - Add license to Javatar\n - [Dev] Add a Java grammar parser. More informations in documentation\n\nYou can report/suggest any issue on Javatar repository. Link is already located in README file."


def get_version():
	return VERSION


def check_news():
	get_action().add_action("javatar.util.news", "Check news")
	from .javatar_utils import get_settings, set_settings, is_stable
	if get_settings("message_id") < NEWSID:
		if get_settings("message_id") != -1:
			if is_stable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar: Package has been updated!\n" + NEWS)
				get_action().add_action("javatar.util.news", "Show stable news")
			elif not is_stable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
				sublime.message_dialog("Javatar [Dev]: Package has been updated!\n" + NEWS)
				get_action().add_action("javatar.util.news", "Show dev news")
			send_usages(get_usage_data())
			set_settings("message_id", NEWSID)
		elif get_settings("javatar_gp") & 0x1 == 0:
			send_usages(get_usage_data(), True)
