import sublime_plugin
from ..utils import *


class JavatarCallCommand(sublime_plugin.TextCommand):
    def run(self, edit, type=""):
        getAction().addAction("javatar.command.call.run", "Call [type=" + type + "]")
        if not isJava():
            sublime.error_message("Current file is not Java")
            return
        sels = self.view.sel()
        for sel in sels:
            if type == "package_name":
                self.view.insert(edit, sel.a, getCurrentPackage())
            elif type == "subpackage_name":
                self.view.insert(edit, sel.a, getCurrentPackage().split(".")[-1])
            elif type == "full_class_name":
                self.view.insert(edit, sel.a, normalizePackage(getCurrentPackage()+"."+getPath("name", getPath("current_file"))[:-5]))
            elif type == "class_name":
                self.view.insert(edit, sel.a, getPath("name", getPath("current_file"))[:-5])

    def description(self, type=""):
        if type == "package_name":
            return "Insert Package Name"
        elif type == "subpackage_name":
            return "Insert Subpackage Name"
        elif type == "full_class_name":
            return "Insert Full Class Name"
        elif type == "class_name":
            return "Insert Class Name"
        return None