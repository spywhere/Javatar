import os
import sublime_plugin
from Javatar.utils import *


def MakePackage(current_dir, package):
    package_dir = package.split(".")
    package_dir.insert(0, current_dir)
    target_dir = "/".join(package_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir


class JavatarCreatePackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = self.window.show_input_panel("Package Name:", "", self.createPackage, "", "")
        view.set_name("JavatarCreatePackage")

    def createPackage(self, text):
        target_dir = MakePackage(getPath("project_dir"), text)
        showStatus("Package \""+toPackage(target_dir)+"\" is created")
        self.clear()


class JavatarCreateSubpackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = self.window.show_input_panel("Subpackage Name:", "", self.createSubpackage, "", "")
        view.set_name("JavatarCreateSubpackage")

    def createSubpackage(self, text):
        target_dir = MakePackage(getPath("current_dir"), text)
        showStatus("Subpackage \""+toPackage(target_dir)+"\" is created")
        self.clear()
