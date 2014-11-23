import sublime
import sublime_plugin
from ..utils import (
    add_action,
    is_java,
    get_current_package,
    normalize_package,
    get_class_name
)


class JavatarCallCommand(sublime_plugin.TextCommand):
    descriptions = {
        "package_name": "Insert Package Name",
        "subpackage_name": "Insert Subpackage Name",
        "full_class_name": "Insert Full Class Name",
        "class_name": "Insert Class Name"
    }

    def run(self, edit, call_type=""):
        add_action(
            "javatar.command.call.run",
            "Call [call_type=" + call_type + "]"
        )
        if not is_java():
            sublime.error_message("Current file is not Java")
            return
        sels = self.view.sel()
        for sel in sels:
            if call_type == "package_name":
                self.view.insert(edit, sel.a, get_current_package())
            elif call_type == "subpackage_name":
                self.view.insert(edit, sel.a, get_current_package().split(".")[-1])
            elif call_type == "full_class_name":
                self.view.insert(edit, sel.a, normalize_package(get_current_package() + "." + get_class_name()))
            elif call_type == "class_name":
                self.view.insert(edit, sel.a, get_class_name())

    def description(self, call_type=""):
        return self.descriptions.get(call_type, None)
