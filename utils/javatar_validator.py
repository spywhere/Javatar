import sublime
import re


def isJava(file=""):
    from .javatar_utils import getSettings
    view = sublime.active_window().active_view()
    if view is None:
        return False
    if file is "" or file is None:
        file = view.file_name()
    if file is None:
        return False
    return re.match(getSettings("java_file_validation"), file, re.I | re.M) is not None


def isPackage(package):
    from .javatar_utils import getSettings
    return re.match(getSettings("package_name_scope"), package, re.I) is not None


def isProject():
    window = sublime.active_window()
    return window.project_data() is not None


def isFile():
    view = sublime.active_window().active_view()
    return view is not None and view.file_name() is not None
