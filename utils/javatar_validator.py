import sublime
import re


def is_java(filepath=""):
	from .javatar_utils import get_settings
	view = sublime.active_window().active_view()
	if view is None:
		return False
	if filepath is "" or filepath is None:
		filepath = view.file_name()
	else:
		view = None
	isjava = False
	if filepath is not None:
		for extension in get_settings("java_extensions"):
			if filepath.endswith("." + extension):
				return True
	return (view is not None and len(view.find_by_selector(get_settings("java_source_selector"))) > 0)


def is_package(package):
	from .javatar_utils import get_settings
	return re.match(get_settings("package_name_match"), package, re.M) is not None


def is_project(window=None):
	if window is None:
		window = sublime.active_window()
	return len(window.folders()) > 0


def is_file():
	view = sublime.active_window().active_view()
	return view is not None and view.file_name() is not None
