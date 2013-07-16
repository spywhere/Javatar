import sublime
import re


def isJava():
    from .javatar_utils import getSettings
    view = sublime.active_window().active_view()
    return re.match(getSettings("java_file_validation"), view.file_name(), re.I | re.M) is not None


def isPackage(package):
    from .javatar_utils import getSettings
    return re.match(getSettings("package_validation"), package, re.I) is not None


def isProject():
    window = sublime.active_window()
    return window.project_data() is not None


def isFile():
    view = sublime.active_window().active_view()
    return view.file_name() is not None
