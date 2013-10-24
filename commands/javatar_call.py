import sublime_plugin
from Javatar.utils import *


class JavatarCallCommand(sublime_plugin.TextCommand):
    def run(self, edit, type="", contents="", callback=None):
        sels = self.view.sel()
        for sel in sels:
            if type == "package_name":
                self.view.insert(edit, sel.a, getCurrentPackage())
            elif type == "subpackage_name":
                self.view.insert(edit, sel.a, getCurrentPackage().split(".")[-1])
            elif type == "full_class_name":
                if isJava():
                    self.view.insert(edit, sel.a, normalizePackage(getCurrentPackage()+"."+getPath("name", getPath("current_file"))[:-5]))
                else:
                    sublime.error_message("Current file is not Java")
            elif type == "class_name":
                if isJava():
                    self.view.insert(edit, sel.a, getPath("name", getPath("current_file"))[:-5])
                else:
                    sublime.error_message("Current file is not Java")
