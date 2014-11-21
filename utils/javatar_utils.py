from time import clock

import sublime
import os
from os.path import join, basename, dirname, relpath
from copy import deepcopy
from .javatar_actions import *


SETTINGSBASE = None
SETTINGS = None
SUBLIME_SETTINGS = None
STARTUP_TIME = None
LAST_TIMER = None
UPDATE_READY = False


def get_startup_time():
    return STARTUP_TIME


def start_clock():
    global LAST_TIMER
    LAST_TIMER = clock()


def stop_clock(add=True, notify=True):
    global STARTUP_TIME
    if add and STARTUP_TIME is not None:
        STARTUP_TIME += clock() - LAST_TIMER
    else:
        STARTUP_TIME = clock() - LAST_TIMER
    if notify and not is_stable():
        print("[Javatar] Startup Time: {0:.2f}s".format(STARTUP_TIME))


def reset():
    add_action("javatar.util.util.reset", "Reset all settings")
    global SUBLIME_SETTINGS, SETTINGS, SETTINGSBASE
    SUBLIME_SETTINGS = None
    SETTINGS = None
    SETTINGSBASE = None
    from .javatar_collections import reset_snippets_and_packages
    reset_snippets_and_packages()


def is_ready():
    return SETTINGS is not None


def save_project_state(repeat=True):
    if UPDATE_READY and get_settings("allow_project_restoration"):
        project_data = {
            str(window.id()): window.project_data()
            for window in sublime.windows()
        }
        set_settings("project_data", project_data)
        if repeat:
            sublime.set_timeout(save_project_state, get_settings("project_update_interval"))


def restore_project_state():
    global UPDATE_READY
    if get_settings("allow_project_restoration"):
        project_data = get_global_settings("project_data")
        if len(project_data) > 0:
            for window in sublime.windows():
                if str(window.id()) in project_data:
                    window.set_project_data(project_data[str(window.id())])
                    if is_debug():
                        print("[Javatar] Restore project data on window " + str(window.id()))
        UPDATE_READY = True
        save_project_state()


def read_settings(config):
    add_action("javatar.util.util.read_settings", "Read settings")
    global SUBLIME_SETTINGS, SETTINGS, SETTINGSBASE
    SETTINGSBASE = config
    SETTINGS = sublime.load_settings(config)
    SUBLIME_SETTINGS = sublime.load_settings("Preferences.sublime-settings")
    restore_project_state()
    from .javatar_collections import load_snippets_and_packages
    load_snippets_and_packages()


def get_project_settings(key, asList=False):
    project_data = sublime.active_window().project_data()
    if project_data is not None:
        if "javatar" in project_data and key in project_data["javatar"]:
            if asList:
                return [project_data["javatar"][key], True]
            else:
                return project_data["javatar"][key]
        elif key in project_data:
            # Deprecated
            if asList:
                return [project_data[key], True]
            else:
                return project_data[key]
    return None


def get_global_settings(key, asList=False):
    if asList:
        return [SETTINGS.get(key, None), False]
    else:
        return SETTINGS.get(key, None)


def get_sublime_settings(key, default=None):
    return SUBLIME_SETTINGS.get(key, default)


def get_settings(key, asList=False):
    project_settings = get_project_settings(key, asList)
    if project_settings is not None:
        return project_settings
    return get_global_settings(key, asList)


def set_settings(key, val, project=False):
    if project:
        project_data = sublime.active_window().project_data()
        if "javatar" in project_data:
            data = project_data["javatar"]
        else:
            data = {}
        data[key] = val
        project_data["javatar"] = data
        sublime.active_window().set_project_data(project_data)
    else:
        SETTINGS.set(key, val)
        sublime.save_settings(SETTINGSBASE)


def del_settings(key, project=False):
    if project:
        window = sublime.active_window()
        project_data = window.project_data()
        if project_data is not None and "javatar" in project_data and key in project_data["javatar"]:
            del project_data["javatar"][key]
            window.set_project_data(project_data)
    else:
        if SETTINGS.has(key):
            SETTINGS.erase(key)
            sublime.save_settings(SETTINGSBASE)


def is_debug():
    return get_settings("debug_mode")


def is_stable():
    return str.lower(get_settings("package_channel")) != "dev"


def normalize_path(path):
    name = get_path("name", path)
    parent = get_path("parent", path)
    if parent != get_path("parent", parent):
        parent = normalize_path(parent)
    for dir_path in os.listdir(parent):
        if dir_path.lower() == name.lower():
            return get_path("join", parent, dir_path)
    return path


def split_path(path):
    rest, tail = os.path.split(path)
    if len(rest) <= 1:
        return tail,
    return split_path(rest) + (tail,)


def merge_path(pathlist):
    outpath = ""
    for path in pathlist:
        outpath = get_path("join", outpath, path)
    return outpath


def show_notification(message, title="Javatar"):
    sublime.run_command("sub_notify", {"title": title, "msg": message, "sound": True})


def show_status(text, delay=None, require_java=True):
    from .javatar_status import get_status
    get_status().set_status(text, delay, require_java)


def hide_status(clear=True):
    from .javatar_status import get_status
    get_status().hide_status(clear)


def to_readable_size(filepath):
    if filepath[0:8] == "Packages":
        filepath = sublime.packages_path() + filepath[8:]
    scales = [
        [1000 ** 5, "PB"],
        [1000 ** 4, "TB"],
        [1000 ** 3, "GB"],
        [1000 ** 2, "MB"],
        [1000 ** 1, "KB"],
        [1000 ** 0, "B"]
    ]
    filesize = os.path.getsize(filepath)
    for scale in scales:
        if filesize >= scale[0]:
            break
    return str(int(filesize / scale[0] * 100) / 100) + scale[1]


def get_current_package(relative=True):
    from .javatar_validator import is_project, is_file
    if is_file() and get_path("current_dir") is not None:
        return to_package(get_path("current_dir"), relative)
    elif is_project() and get_path("source_folder") is not None:
        return to_package(get_path("source_folder"), relative)
    else:
        return ""


def to_readable_package(package, asPackage=False):
    if not asPackage:
        package = to_package(package)
    if package == "":
        from .javatar_validator import is_project
        if is_project():
            package = "(Default Package)"
        else:
            package = "(Unknown Package)"
    return package


def to_package(path, relative=True):
    if relative:
        path = get_path("relative", path, get_package_root_dir())
    package = ".".join(split_path(path))
    from .javatar_java import normalize_package
    return normalize_package(package)


def get_package_root_dir():
    from .javatar_validator import is_project
    if is_project():
        return get_path("source_folder")
    elif get_path("current_dir") is not None:
        return get_path("current_dir")
    else:
        return ""


def contains_file(directory, file_path):
    return os.path.normcase(os.path.normpath(file_path)).startswith(os.path.normcase(os.path.normpath(directory)))


def without_extension(file_path):
    filename, ext = os.path.splitext(os.path.basename(file_path))
    for extension in get_settings("java_extensions"):
        if ext == extension:
            return file_path[:-len(ext)]
    return file_path


def get_main_class_name(file_path=None, view=None):
    from .javatar_validator import is_file
    if view is not None:
        return without_extension(get_path("name", view.file_name()))
    elif file_path is not None:
        return without_extension(get_path("name", file_path))
    else:
        if is_file():
            return get_main_class_name(None, sublime.active_window().active_view())
    return None


def get_class_name(file_path=None, view=None):
    from .javatar_validator import is_file
    if view is not None:
        classRegions = view.find_by_selector(get_settings("class_name_selector"))
        if len(classRegions) > 0:
            return view.substr(classRegions[0])
        else:
            return without_extension(get_path("name", view.file_name()))
    elif file_path is not None:
        return without_extension(get_path("name", file_path))
    else:
        if is_file():
            return get_class_name(None, sublime.active_window().active_view())
    return None


def parse_macro(text, macro_data=None, file_path=None):
    if file_path is not None:
        text = text.replace("$file_parent", get_path("parent", file_path))
        text = text.replace("$file_name", get_path("name", file_path))
        text = text.replace("$file", file_path)
    if macro_data is not None:
        for key in macro_data:
            text = text.replace("$" + key, macro_data[key])
    return text


def get_macro_data(class_name=None):
    if class_name is None:
        class_name = get_class_name()
    from .javatar_java import normalize_package
    from .javatar_validator import is_file
    source_data = {
        "project_dir": get_path("project_dir"),
        "source_folder": get_path("source_folder"),
        "packages_path": sublime.packages_path(),
        "sep": os.sep,
    }
    if is_file():
        source_data.update({
            "full_class_path": normalize_package(get_current_package() + "." + class_name),
            "class_name": get_class_name(),
            "package": get_current_package()
        })
    return source_data


def get_javatar_parent():
    return __name__.split('.')[0]


def get_current_file():
    return sublime.active_window().active_view().file_name()


def get_source_folder():
    return get_settings("source_folder") or get_project_dir()


def get_project_dir():
    from .javatar_validator import is_file

    path = get_current_dir()
    folders = sublime.active_window().folders()

    if len(folders) == 1:
        return folders[0]

    elif len(folders) > 1:
        if path is None:
            path = folders[0]
        for folder in folders:
            if is_file() and contains_file(folder, get_current_file()):
                return folder

    return path


def get_current_dir():
    if get_current_file() is not None:
        return dirname(get_current_file())
    else:
        return None


class JavatarMergedDict():
    def __init__(self, dict1, dict2):
        self.global_dict = dict1
        self.local_dict = dict2

    def get_dict(self, custom=None):
        if self.global_dict is None:
            global_dict = {}
        else:
            global_dict = deepcopy(self.global_dict)
        if self.local_dict is not None:
            if custom is not None:
                return custom(global_dict, self.local_dict)
            for setting in self.local_dict:
                global_dict[setting] = self.local_dict[setting]
        if global_dict is not None and len(global_dict) > 0:
            return global_dict
        else:
            return None

    def get(self, key):
        if self.local_dict is not None and key in self.local_dict:
            return self.local_dict[key]
        elif self.global_dict is not None and key in self.global_dict:
            return self.global_dict[key]
        return None

    def has(self, key):
        return (self.local_dict is not None and key in self.local_dict) or (self.global_dict is not None and key in self.global_dict)

    def set(self, key, val, follow_level=True):
        # Follow level:
        # Set global only, except specified
        # Remove local then global
        if val is None:
            if self.local_dict is not None and key in self.local_dict and follow_level:
                del self.local_dict[key]
            elif key in self.global_dict:
                del self.global_dict[key]
        else:
            if follow_level:
                if self.global_dict is None:
                    self.global_dict = {}
                self.global_dict[key] = val
            else:
                if self.local_dict is None:
                    self.local_dict = {}
                self.local_dict[key] = val

    def get_local_dict(self):
        if self.local_dict is not None and len(self.local_dict) > 0:
            return self.local_dict
        else:
            return None

    def get_global_dict(self):
        if self.global_dict is not None and len(self.global_dict) > 0:
            return self.global_dict
        else:
            return None


class JavatarDict():
    def __init__(self, dict1):
        self.jdict = dict1

    def get_dict(self, custom=None):
        return self.jdict

    def get(self, key):
        if self.jdict is not None and key in self.jdict:
            return self.jdict[key]
        return None

    def has(self, key):
        return (self.jdict is not None and key in self.jdict)

    def set(self, key, val, to_global=False):
        if val is None and self.jdict is not None and key in self.jdict and to_global:
            del self.jdict[key]
        else:
            if self.jdict is None:
                self.jdict = {}
            self.jdict[key] = val

    def get_local_dict(self):
        return None

    def get_global_dict(self):
        return self.jdict
