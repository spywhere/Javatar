import sublime_plugin
from Javatar.utils import *


class JavatarCallCommand(sublime_plugin.TextCommand):
    call_list = [["Package Name", "Return package path from root"], ["Subpackage Name", "Return current package name"], ["Full Class Name", "Return class path from root"], ["Class Name", "Return current class name"]]

    def run(self, edit, type="", contents="", callback=None):
        sels = self.view.sel()
        for sel in sels:
            if type == "package_name":
                self.view.insert(edit, sel.a, "Package.Subpackage")
            elif type == "subpackage_name":
                self.view.insert(edit, sel.a, "MyPackage")
            elif type == "full_class_name":
                self.view.insert(edit, sel.a, "Package.Class")
            elif type == "class_name":
                self.view.insert(edit, sel.a, "MyClass")
            elif type == "javatar_insert":  # Please do not use this in user level except for plugin requests
                self.view.insert(edit, 0, contents)
                callback
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
