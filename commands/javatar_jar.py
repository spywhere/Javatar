import sublime_plugin
from Javatar.utils import *


class JavatarCreateJarFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create JAR File")


class JavatarCreateExeJarFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Executable JAR File")
