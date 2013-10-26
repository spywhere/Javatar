import sublime_plugin
from ..utils import *


class JavatarCreatePackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = sublime.active_window().show_input_panel("Package Name:", "", self.createPackage, "", "")
        view.set_name("JavatarCreatePackage")

    def createPackage(self, text):
        getAction().addAction("javatar.command.package.create_package", "Create package [package="+text+"]")
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

        target_dir = makePackage(getPackageRootDir(relative), text)
        showStatus("Package \""+toPackage(target_dir)+"\" is created")
