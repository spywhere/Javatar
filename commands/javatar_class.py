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

    makePackage(getPackageRootDir(), packageAsDirectory(package), True)
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
    data = re.sub("%class%", info["class"], data)
    data = re.sub("%file%", info["file"], data)
    data = re.sub("%file_name%", getPath("name", info["file"]), data)
    data = re.sub("%package_path%", getCurrentPackage(), data)
    return data


def setSelection(view, focus):
    view.sel().clear()
    view.sel().add(sublime.Region(focus.start(), focus.start()))


def createClassFile(file, contents, msg):
    if os.path.exists(file):
        sublime.error_message(msg)
        return
    open(file, "w")
    view = sublime.active_window().open_file(file)
    view.set_syntax_file("Packages/Java/Java.tmLanguage")
    focus = re.search("%focus%", contents, re.I | re.M)
    contents = re.sub("%focus%", "", contents)
    sublime.set_timeout(lambda: view.run_command("javatar_call", {"type": "javatar_insert", "contents": contents}), 100)
    sublime.set_timeout(lambda: setSelection(view, focus), 100)
    sublime.set_timeout(lambda: view.run_command("save"), 100)


class JavatarCreateClassCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = sublime.active_window().show_input_panel("Class Name:", "", self.createClass, "", "")
        view.set_name("JavatarCreateClass")

    def createClass(self, text):
        info = getInfo(text)
        createClassFile(info["file"], getFileContents("Class.javatar", info), "Class already exists")
        sublime.set_timeout(lambda: showStatus("Class \"" + info["class"] + "\" is created within package \"" + toReadablePackage(info["package"], True) + "\""), 500)


class JavatarCreateInterfaceCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = sublime.active_window().show_input_panel("Interface Name:", "", self.createInterface, "", "")
        view.set_name("JavatarCreateInterface")

    def createInterface(self, text):
        info = getInfo(text)
        createClassFile(info["file"], getFileContents("Interface.javatar", info), "Interface already exists")
        sublime.set_timeout(lambda: showStatus("Interface \"" + info["class"] + "\" is created within package \"" + toReadablePackage(info["package"], True) + "\""), 500)


class JavatarCreateEnumCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = sublime.active_window().show_input_panel("Enumerator Name:", "", self.createEnum, "", "")
        view.set_name("JavatarCreateEnum")

    def createEnum(self, text):
        info = getInfo(text)
        createClassFile(info["file"], getFileContents("Enumerator.javatar", info), "Enumerator already exists")
        sublime.set_timeout(lambda: showStatus("Enumerator \"" + info["class"] + "\" is created within package \"" + toReadablePackage(info["package"], True) + "\""), 500)
