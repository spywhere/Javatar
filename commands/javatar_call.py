import sublime_plugin
from Javatar.utils import *


class JavatarCallCommand(sublime_plugin.TextCommand):
    call_list = [["Package Name", "Return package path from root"], ["Subpackage Name", "Return current package name"], ["Full Class Name", "Return class path from root"], ["Class Name", "Return current class name"]]

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
            elif type == "class_name":
                if isJava():
                    self.view.insert(edit, sel.a, getPath("name", getPath("current_file"))[:-5])
            else:
                self.view.window().show_quick_panel(self.call_list, self.call)

    def call(self, index=-1):
        if index == 0:
            self.view.run_command("javatar_call", {"type": "package_name"})
        elif index == 1:
            self.view.run_command("javatar_call", {"type": "subpackage_name"})
        elif index == 2:
            self.view.run_command("javatar_call", {"type": "full_class_name"})
        elif index == 3:
            self.view.run_command("javatar_call", {"type": "class_name"})
