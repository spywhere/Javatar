import sublime
import os
from .javatar_actions import *


VERSION = "13.10.27.0.59b"
STATUS = "Javatar"
SETTINGSBASE = None
SETTINGS = None


def getVersion():
    return VERSION


def reset():
    getAction().addAction("javatar.util.util.reset", "Reset all settings")
    global SETTINGS, SETTINGSBASE
    SETTINGS = None
    SETTINGSBASE = None
    from .javatar_collections import resetSnippets
    resetSnippets()


def isReady():
    return SETTINGS is not None

def readSettings(config):
    getAction().addAction("javatar.util.util.read_settings", "Read settings")
    global SETTINGS, SETTINGSBASE
    SETTINGSBASE = config
    SETTINGS = sublime.load_settings(config)
    from .javatar_collections import getSnippetFiles
    getSnippetFiles()


def getSettings(key):
    return SETTINGS.get(key)


def setSettings(key, val):
    SETTINGS.set(key, val)
    sublime.save_settings(SETTINGSBASE)


def isStable():
    return str.lower(getSettings("package_channel")) == "stable"


def normalizePath(path):
    name = getPath("name", path)
    parent = getPath("parent", path)
    if parent != getPath("parent", parent):
        parent = normalizePath(parent)
    for dir in os.listdir(parent):
        if dir.lower() == name:
            return getPath("join", parent, dir)
    return path


def splitPath(path):
    rest, tail = os.path.split(path)
    if len(rest) <= 1:
        return tail,
    return splitPath(rest) + (tail,)


def mergePath(pathlist):
    outpath = ""
    for path in pathlist:
        outpath = getPath("join", outpath, path)
    return outpath


def showStatus(text, delay=None):
    if delay is None:
        delay = getSettings("status_delay")
    from .javatar_validator import isJava
    if not isJava():
        return
    view = sublime.active_window().active_view()
    view.set_status(STATUS, text)
    if delay >= 0:
        sublime.set_timeout(hideStatus, delay)


def hideStatus():
    view = sublime.active_window().active_view()
    from .javatar_validator import isJava
    if not isJava():
        return
    if getSettings("show_package_path"):
        view.set_status(STATUS, "Package: " + toReadablePackage(getCurrentPackage(), True))
    else:
        view.erase_status(STATUS)


def getCurrentPackage(relative=False):
    from .javatar_validator import isProject, isFile
    if not relative and isFile() and getPath("current_dir") is not None:
        return toPackage(getPath("current_dir"))
    elif not relative and isProject() and getPath("project_dir") is not None:
        return toPackage(getPath("project_dir"))
    else:
        return ""


def toReadablePackage(package, asPackage=False):
    if not asPackage:
        package = toPackage(package)
    if package == "":
        from .javatar_validator import isProject
        if isProject():
            package = "(Default Package)"
        else:
            package = "(Unknown Package)"
    return package


def toPackage(dir):
    dir = os.path.relpath(dir, getPackageRootDir())
    package = ".".join(splitPath(dir))
    while package.startswith("."):
        package = package[1:]
    return package


def getPackageRootDir(isSub=False):
    from .javatar_validator import isProject, isFile
    if isFile() and isSub:
        return getPath("current_dir")
    elif isProject():
        return getPath("project_dir")
    elif getPath("current_dir") is not None:
        return getPath("current_dir")
    else:
        return ""


def containsFile(directory, file):
    return os.path.normcase(os.path.normpath(file)).startswith(os.path.normcase(os.path.normpath(directory)))


def getPath(type="", dir="", dir2=""):
    window = sublime.active_window()
    if type == "project_dir":
        from .javatar_validator import isFile
        path = ""
        folders = window.folders()
        if len(folders) == 1:
            return folders[0]
        for folder in folders:
            if isFile() and containsFile(folder, getPath("current_file")):
                path = folder
                break
        return path
    elif type == "current_dir":
        if getPath("current_file") is not None:
            return getPath("parent", getPath("current_file"))
        else:
            return None
    elif type == "current_file":
        return window.active_view().file_name()
    elif type == "parent":
        return os.path.dirname(dir)
    elif type == "name":
        return os.path.basename(dir)
    elif type == "join":
        return os.path.join(dir, dir2)
    elif type == "exist":
        return os.path.exists(dir)
    elif type == "javatar_parent":
        name = __name__.split('.')
        return name[0]
    else:
        return ""
