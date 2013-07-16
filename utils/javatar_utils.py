import os
import sublime


STATUS = "Javatar"
SETTINGS = None


def readSettings(config):
    global SETTINGS
    SETTINGS = config


def getSettings(key):
    return SETTINGS.get(key)


def showStatus(text, delay=5000):
    view = sublime.active_window().active_view()
    view.set_status(STATUS, text)
    if delay >= 0:
        sublime.set_timeout(hideStatus, delay)


def hideStatus():
    view = sublime.active_window().active_view()
    if getSettings("show_package_path"):
        view.set_status(STATUS, toPackage(getPath("current_dir")))
    else:
        view.erase_status(STATUS)


def toPackage(dir):
    dir = os.path.relpath(dir, getPath("project_dir"))
    package = ".".join(dir.split("/"))
    if package.startswith("."):
        package = package[1:]
    return package


def getPath(type="", dir=""):
    window = sublime.active_window()
    if type == "project_dir":
        project_data = window.project_data()
        folder_entries = []
        folders = ""
        if project_data is not None:
            folder_entries = project_data.get("folders", [])
        for index in range(len(folder_entries)):
            folder_entry = folder_entries[index]
            if "path" in folder_entry:
                return folder_entry["path"]
        return folders
    elif type == "current_dir":
        return getPath("parent", getPath("current_file"))
    elif type == "current_file":
        return window.active_view().file_name()
    elif type == "parent":
        return os.path.dirname(dir)
    elif type == "name":
        return os.path.basename(dir)
    else:
        return ""
