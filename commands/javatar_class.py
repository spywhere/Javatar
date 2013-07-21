import os
import re
import sublime
import sublime_plugin
from Javatar.utils import *


def getInfo(text):
    relative = True
    if text.startswith("~"):
        text = text[1:]
        relative = False

    if not isProject() and not isFile():
        sublime.error_message("Unknown package location")
        return
    if not isPackage(text):
        sublime.error_message("Invalid package naming")
        return

    package = normalizePackage(getCurrentPackage(not relative) + "." + getPackagePath(text))
    className = getClassName(text)

    target_dir = makePackage(getPackageRootDir(), packageAsDirectory(package), True)
    target_dir = normalizePath(target_dir)
    package = toPackage(target_dir)
    file = getPath("join", getPackageRootDir(), getPath("join", packageAsDirectory(package), className + ".java"))
    return {"file": file, "package": package, "class": className, "relative": relative}


def getFileContents(file, info):
    filename = getSnippet(file)
    if filename == "":
        sublime.error_message("Snippet \"" + file + "\" not found")
        return ""
    f = open(filename, "r")
    data = f.read()
    if info["package"] != "":
        data = re.sub("%package%", "package " + info["package"] + ";", data)
    else:
        data = re.sub("%package%", "", data)
    data = re.sub("%class%", info["class"], data)
    data = re.sub("%file%", info["file"], data)
    data = re.sub("%file_name%", getPath("name", info["file"]), data)
    data = re.sub("%package_path%", getCurrentPackage(), data)
    return data


def setSelection(view, focus):
    view.sel().clear()
    view.sel().add(sublime.Region(focus.start()))


def insertAndSave(view, contents):
    view.run_command("insert_snippet", {"contents": contents})
    view.run_command("save")


def createClassFile(file, contents, msg):
    if os.path.exists(file):
        sublime.error_message(msg)
        return
    open(file, "w")
    view = sublime.active_window().open_file(file)
    view.set_syntax_file("Packages/Java/Java.tmLanguage")
    sublime.set_timeout(lambda: insertAndSave(view, contents), 100)


class JavatarCreateCommand(sublime_plugin.WindowCommand):
    def run(self, text="", type=""):
        if type != "":
            self.showInput(-1, type)
            return
        if text != "":
            info = getInfo(text)
            createClassFile(info["file"], getFileContents(self.type, info), self.type + "\"" + info["class"] + "\" already exists")
            sublime.set_timeout(lambda: showStatus(self.type + " \"" + info["class"] + "\" is created within package \"" + toReadablePackage(info["package"], True) + "\""), 500)
        else:
            sublime.active_window().show_quick_panel(getSnippetList(), self.showInput)

    def showInput(self, index, type=""):
        if type != "" or index >= 0:
            if type != "":
                self.type = type
            else:
                self.type = getSnippetName(index)
            view = sublime.active_window().show_input_panel(self.type + " Name:", "", self.run, "", "")
            view.set_name("JavatarCreate")
