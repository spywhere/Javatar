import sublime_plugin
from Javatar.utils import *


class JavatarBuildProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Build Project")
