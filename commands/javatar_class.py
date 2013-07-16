import sublime_plugin
from Javatar.utils import *


class JavatarCreateClassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Class")


class JavatarCreateInterfaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Interface")


class JavatarCreateEnumCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Enum")
