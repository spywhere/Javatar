import sublime
from .javatar_actions import *
from .javatar_updater import *
from .javatar_usage import send_usages, get_usage_data, start_clock, stop_clock


# YY.MM.DD.HH.MM
VERSION = "14.09.26.13.45b"
UPDATEFOR = "all"
NEWSID = 18


def get_version():
	return VERSION


def show_news(title, prefix=""):
	news = ("Just install Javatar? Checkout JavatarDoc for Javatar information and guides. Link is located in README file.\n\n"
			"A small update but got a new improvement on class creation. Be sure to checkout JavaDoc!\n"
			"These are updates and fixes for Javatar " + VERSION + "...\n"
			"- Build notification via SubNotify (more details in JavatarDoc)\n"
			"- Fix Javatar Shell cause Sublime Text crash on output encoding error\n"
			"- Javatar Shell will now scroll to bottom\n"
			"- Class creation improvements (See JavaDoc for more information)\n"
			"- Remove abstract class snippets since a new class creation improvement can do more!\n\n"
			"You can report/suggest any issue on Javatar repository. Link is already located in README file.")
	view = sublime.active_window().new_file()
	view.set_name(title)
	view.run_command("javatar_util", {"util_type": "add", "text": prefix+news})
	view.set_read_only(True)
	view.set_scratch(True)


def check_news():
	get_action().add_action("javatar.util.news", "Check news")
	from .javatar_utils import get_settings, set_settings, is_stable
	if get_settings("message_id") < NEWSID:
		if get_settings("message_id") != -1:
			stop_clock(notify=False)
			if is_stable() and (UPDATEFOR == "stable" or UPDATEFOR == "all"):
				show_news("Javatar: Package has been updated!")
				get_action().add_action("javatar.util.news", "Show stable news")
			elif not is_stable() and (UPDATEFOR == "dev" or UPDATEFOR == "all"):
				show_news("Javatar [Dev]: Package has been updated!")
				get_action().add_action("javatar.util.news", "Show dev news")
			start_clock()
			send_usages(get_usage_data())
			set_settings("message_id", NEWSID)
		elif get_settings("javatar_gp") & 0x1 == 0:
			send_usages(get_usage_data(), True)
