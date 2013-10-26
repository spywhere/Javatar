import sublime_plugin
from ..QuickMenu import *
from ..utils.javatar_actions import *

class JavatarCommand(sublime_plugin.WindowCommand):
    qm = None
    menuStable = {
        "main": {
            "items": [["Builds...", "Build system"], ["Calls...", "Insert class informations"], ["Create...", "Create a new class"], ["Operations...", "Do a Java operations"]],
            "actions": [
                {
                    "name": "builds"
                }, {
                    "name": "calls"
                }, {
                    "name": "creates"
                }, {
                    "name": "operations"
                }
            ]
        },
        "builds": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Project", "Build all classes in project"], ["Package", "Build all classes in current package"], ["Current Class", "Build current class"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_build",
                    "args": {
                        "type": "project"
                    }
                }, {
                    "command": "javatar_build",
                    "args": {
                        "type": "package"
                    }
                }, {
                    "command": "javatar_build",
                    "args": {
                        "type": "class"
                    }
                }
            ]
        },
        "calls": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Package Name", "Return package path from root"], ["Subpackage Name", "Return current package name"], ["Full Class Name", "Return class path from root"], ["Class Name", "Return current class name"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_call",
                    "args": {
                        "type": "package_name"
                    }
                }, {
                    "command": "javatar_call",
                    "args": {
                        "type": "subpackage_name"
                    }
                }, {
                    "command": "javatar_call",
                    "args": {
                        "type": "full_class_name"
                    }
                }, {
                    "command": "javatar_call",
                    "args": {
                        "type": "class_name"
                    }
                }
            ]
        },
        "creates": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"],["Package", "Create a new package"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_create_package"
                }
            ]
        },
        "operations": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Correct Class", "Correct package and class name in current file"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_correct_class"
                }
            ]
        },
        "dev": {
            "items": [["Back", "Back to previous menu"], ["Operations: Organize Imports", "Correct class imports in current file"], ["Operations: Rename Class", "Rename current class"], ["Operations: Rename Package", "Rename current package"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_organize_imports"
                }, {
                    "command": "javatar_rename_operation",
                    "args": {
                        "type": "class"
                    }
                }, {
                    "command": "javatar_rename_operation",
                    "args": {
                        "type": "package"
                    }
                }
            ]
        },
        "help": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Actions History", "Generate a report on Javatar actions history"], ["Actions History (Custom)", "Generate a report on Javatar actions history using custom selector"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_help",
                    "args": {
                        "action": "actions_history",
                        "selector": ""
                    }
                }, {
                    "command": "javatar_help",
                    "args": {
                        "action": "actions_history"
                    }
                }
            ]
        }
    }

    def run(self, menu=None, action=None):
        if self.qm is None:
            from ..utils import getSnippetList, isStable
            self.qm = QuickMenu(self.menuStable)
            # Create a menu for development channel
            if not isStable():
                self.qm.addItems("main", [["Development Section...", "All testing features"]], [{"name":"dev"}])

            # Generate action for Create menu
            actions = []
            for snippet in getSnippetList():
                actions += [{"command":"javatar_create","args":{"type":snippet[0]}}]
            self.qm.addItems("creates", getSnippetList(), actions)

            # Always add Help and Support at the end
            self.qm.addItems("main", [["Help and Support...", "Utilities for Help and Support on Javatar"]], [{"name":"help"}])
        self.qm.show(self.window, None, menu, action)

    def select(self, info):
        if info["index"] < 0:
            getAction().addAction("javatar.menu", "Exit menu [from_sublime="+str(info["from_sublime"])+"]")
        else:
            getAction().addAction("javatar.menu", "Select item "+ str(info["items"][info["index"]]) +" [from_sublime="+str(info["from_sublime"])+"]")