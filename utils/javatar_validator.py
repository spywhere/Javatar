import sublime
import re


def isJava(filepath=""):
	from .javatar_utils import getSettings
	view = sublime.active_window().active_view()
	if view is None:
		return False
	if filepath is "" or filepath is None:
		filepath = view.file_name()
	else:
		view = None
	return (view is not None and len(view.find_by_selector(getSettings("java_source_selector"))) > 0) or (filepath is not None and re.match(getSettings("java_file_validation"), filepath, re.M) is not None)


def isPackage(package):
	from .javatar_utils import getSettings
	return re.match(getSettings("package_name_match"), package, re.M) is not None


def isProject(window=None):
	if window is None:
		window = sublime.active_window()
	return len(window.folders()) > 0


def isFile():
	view = sublime.active_window().active_view()
	return view is not None and view.file_name() is not None
