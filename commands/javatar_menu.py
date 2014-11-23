import sublime_plugin
from ..QuickMenu import *
from ..utils.javatar_actions import *


class JavatarCommand(sublime_plugin.WindowCommand):
    qm = None
    menuStable = {
        "main": {
            "items": [["Builds...", "Build system"], ["Calls...", "Insert class informations"], ["Create...", "Create a new class or package"], ["Operations...", "Do a Java operation"], ["Project Settings...", "Adjust per-project settings"], ["Javatar Settings...", "Adjust Javatar settings"], ["Packages Manager...", "Javatar packages manager"]],
            "actions": [
                {
                    "name": "builds"
                }, {
                    "name": "calls"
                }, {
                    "name": "creates"
                }, {
                    "name": "operations"
                }, {
                    "name": "project_settings"
                }, {
                    "name": "global_settings"
                }, {
                    "name": "package_manager"
                }
            ]
        },
        "builds": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Project", "Build all classes in project"], ["Package", "Build all classes in current package"], ["Working", "Build all classes in opened tabs"], ["Current Class", "Build current class"], ["Run Main Class", "Run class contains main method"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_build",
                    "args": {
                        "build_type": "project"
                    }
                }, {
                    "command": "javatar_build",
                    "args": {
                        "build_type": "package"
                    }
                }, {
                    "command": "javatar_build",
                    "args": {
                        "build_type": "working"
                    }
                }, {
                    "command": "javatar_build",
                    "args": {
                        "build_type": "class"
                    }
                }, {
                    "command": "javatar_run_main"
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
                        "call_type": "package_name"
                    }
                }, {
                    "command": "javatar_call",
                    "args": {
                        "call_type": "subpackage_name"
                    }
                }, {
                    "command": "javatar_call",
                    "args": {
                        "call_type": "full_class_name"
                    }
                }, {
                    "command": "javatar_call",
                    "args": {
                        "call_type": "class_name"
                    }
                }
            ]
        },
        "creates": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Package", "Create a new package"]],
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
        "project_settings": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Set Program Arguments", "Set the arguments to pass on main execution"], ["Dependencies...", "Manage project dependencies"], ["Set Source Folder", "Set source folder to specified as default package"], ["Set Default JDK", "Set default JDK for builds and runs"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "set_program_arguments"
                    }
                }, {
                    "name": "local_dependencies"
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "set_source_folder"
                    }
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "set_jdk",
                        "arg1": True
                    }
                }
            ]
        },
        "global_settings": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Dependencies...", "Manage default dependencies"], ["Set Default JDK", "Set default JDK for builds and runs"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "name": "global_dependencies"
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "set_jdk",
                        "arg1": False
                    }
                }
            ]
        },
        "local_dependencies": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Add External .jar", "Add dependency .jar file"], ["Add Class Folder", "Add dependency class folder"]],
            "actions": [
                {
                    "name": "project_settings"
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "add_external_jar",
                        "arg1": True
                    }
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "add_class_folder",
                        "arg1": True
                    }
                }
            ]
        },
        "global_dependencies": {
            "selected_index": 2,
            "items": [["Back", "Back to previous menu"], ["Add External .jar", "Add dependency .jar file"], ["Add Class Folder", "Add dependency class folder"]],
            "actions": [
                {
                    "name": "global_settings"
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "add_external_jar",
                        "arg1": False
                    }
                }, {
                    "command": "javatar_settings",
                    "args": {
                        "actiontype": "add_class_folder",
                        "arg1": False
                    }
                }
            ]
        },
        "package_manager": {
            "selected_index": 1,
            "items": [["Back", "Back to previous menu"], ["Install Packages...", "Download and install new packages"], ["Uninstall Packages...", "Uninstall installed packages"], ["Reload and Update packages", "Reload all packages and update packages list"], ["Package Tools...", "Tools for package creator"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "name": "install_packages"
                }, {
                    "name": "uninstall_packages"
                }, {
                    "command": "javatar_reload_packages"
                }, {
                    "name": "package_tools"
                }
            ]
        },
        "package_tools": {
            "selected_index": 1,
            "items": [["Back", "Back to previous menu"], ["Create new Javatar Packages", "Create a new .javatar-packages"], ["Generate SHA-256 Hash", "Calculate checksum for current document"], ["Generate SHA-256 Hash from URL", "Calculate checksum from url"], ["Convert Imports", "Convert Javatar Imports to Javatar Packages"]],
            "actions": [
                {
                    "name": "package_manager"
                }, {
                    "command": "javatar_create_javatar_package"
                }, {
                    "command": "javatar_util",
                    "args": {
                        "util_type": "hash"
                    }
                }, {
                    "command": "javatar_util",
                    "args": {
                        "util_type": "remote_hash"
                    }
                }, {
                    "command": "javatar_convert"
                }
            ]
        },
        "install_packages": {
            "selected_index": 1,
            "items": [["Back", "Back to previous menu"], ["No package available", "Please check back later"]],
            "actions": [
                {
                    "name": "package_manager"
                }, {
                }
            ]
        },
        "uninstall_packages": {
            "selected_index": 1,
            "items": [["Back", "Back to previous menu"], ["No package available", "Please check back later"]],
            "actions": [
                {
                    "name": "package_manager"
                }, {
                }
            ]
        },
        "dev": {
            "items": [["Back", "Back to previous menu"], ["Operations: Organize Imports", "Correct class imports in current file"], ["Operations: Rename Class", "Rename current class"], ["Operations: Rename Package", "Rename current package"], ["Parse Document", "Parse Java grammar on current document (may slow Sublime Text)"], ["Prettify JSON", "Reformat current document as pretty JSON"], ["Testing", "For testing and experimenting new feature"]],
            "actions": [
                {
                    "name": "main"
                }, {
                    "command": "javatar_organize_imports"
                }, {
                    "command": "javatar_rename_operation",
                    "args": {
                        "rename_type": "class"
                    }
                }, {
                    "command": "javatar_rename_operation",
                    "args": {
                        "rename_type": "package"
                    }
                }, {
                    "command": "javatar_util",
                    "args": {
                        "util_type": "parse"
                    }
                }, {
                    "command": "javatar_util",
                    "args": {
                        "util_type": "tojson"
                    }
                }, {
                    "command": "javatar_util",
                    "args": {
                        "util_type": "json_test"
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

    def run(self, menu=None, action=None, replaceMenu=None):
        if self.qm is None:
            from ..utils import get_snippet_list, is_stable, is_debug
            self.qm = QuickMenu(self.menuStable)
            # Create a menu for development channel
            if not is_stable():
                self.qm.addItems("main", [["Development Section...", "All testing features"]], [{"name": "dev"}])

            # Generate action for Create menu
            actions = []
            for snippet in get_snippet_list():
                actions += [{"command": "javatar_create", "args": {"create_type": snippet[0]}}]
            self.qm.addItems("creates", get_snippet_list(), actions)

            # Always add Help and Support at the end
            self.qm.addItems("main", [["Help and Support...", "Utilities for Help and Support on Javatar"]], [{"name": "help"}])

            # Quick reload menu
            if is_debug():
                self.qm.insertItem("main", 0, ["Reload Javatar", "Reload Javatar modules (debug only)"], {"command": "javatar_util", "args": {"util_type": "reload"}})
            from ..utils.javatar_news import get_version
            self.qm.addItems("help", [["Javatar", "v" + get_version()]], [{}])
        if replaceMenu is not None:
            self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
            return
        self.qm.show(self.window, self.select, menu, action)

    def select(self, info):
        if info["index"] < 0:
            add_action(
                "javatar.command.menu.select",
                "Exit menu [from_sublime={}]".format(
                    info["from_sublime"]
                )
            )
        else:
            add_action(
                "javatar.command.menu.select",
                "Select item {} [from_sublime={}]".format(
                    info["items"][info["index"]],
                    info["from_sublime"]
                )
            )
