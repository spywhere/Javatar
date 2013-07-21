import sublime_plugin
from Javatar.utils import *


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
        target_dir = makePackage(getPackageRootDir(), text)
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
        target_dir = makePackage(getPackageRootDir(True), text)
        showStatus("Subpackage \""+toPackage(target_dir)+"\" is created")
