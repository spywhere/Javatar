import os.path

import sublime
import re


# Check if it is a Java or not, by checking current syntax (this help on new view calls)
# Better unsave file detection (currently, create a untitled Java file within project is somehow save to wrong dir)


def is_java(filepath=""):
    from .javatar_utils import get_settings

    view = sublime.active_window().active_view()

    if filepath is None or filepath is "":
        if view is None:
            return False
        filepath = view.file_name()

    if filepath is not None:
        _, ext = os.path.splitext(os.path.basename(filepath))

        return ext in get_settings("java_extensions")

    return (view is not None and len(view.find_by_selector(get_settings("java_source_selector"))) > 0)


def is_package(package, special=False):
    from .javatar_utils import get_settings

    pattern = get_settings(
        "special_package_name_match" if special
        else "package_name_match"
    )

    return re.match(pattern, package, re.M) is not None


def is_project(window=None):
    if window is None:
        window = sublime.active_window()
    return len(window.folders()) > 0


def is_file():
    view = sublime.active_window().active_view()
    return view is not None and view.file_name() is not None
