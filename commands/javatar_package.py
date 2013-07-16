import os
import sublime_plugin
from Javatar.utils import *


def MakePackage(current_dir, package):
    package_dir = package.split(".")
    package_dir.insert(0, current_dir)
    target_dir = "/".join(package_dir)
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
        except BaseException as e:
            sublime.error_message("Error while create a package: " + str(e))
    else:
        sublime.message_dialog("Package is already exists")
    return target_dir


class JavatarCreatePackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = sublime.active_window().show_input_panel("Package Name:", "", self.createPackage, "", "")
        view.set_name("JavatarCreatePackage")

    def createPackage(self, text):
        if not isProject() and not isFile():
            sublime.error_message("Unknown package location")
            return
        if not isPackage(text):
            sublime.error_message("Invalid package naming")
            return
        target_dir = MakePackage(getPackageRootDir(), text)
        showStatus("Package \""+toPackage(target_dir)+"\" is created")


class JavatarCreateSubpackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = sublime.active_window().show_input_panel("Subpackage Name:", "", self.createSubpackage, "", "")
        view.set_name("JavatarCreateSubpackage")

    def createSubpackage(self, text):
        if not isFile():
            sublime.error_message("Unknown package location")
            return
        target_dir = MakePackage(getPackageRootDir(True), text)
        showStatus("Subpackage \""+toPackage(target_dir)+"\" is created")
