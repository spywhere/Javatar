import re
import sublime
import threading
from .javatar_actions import *
from .javatar_thread import *
from .javatar_utils import to_readable_size, get_project_settings, get_global_settings, get_path


INSTALLED_PACKAGES = []
SNIPPETS = []
DEFAULT_PACKAGES = []

'''
Allow to include a javatar-packages files into project (atleast easier for bukkit autocomplete)
Allow a new javatar format for packaging a custom jar file (atleast easier for bukkit plugin jar file)
'''


def reset_snippets_and_packages():
    add_action(
        "javatar.util.collection.reset", "Reset all snippets"
    )
    global SNIPPETS
    SNIPPETS = []
    reset_packages()


def reset_packages():
    add_action(
        "javatar.util.collection.reset", "Reset all default packages"
    )
    global INSTALLED_PACKAGES, DEFAULT_PACKAGES
    INSTALLED_PACKAGES = []
    DEFAULT_PACKAGES = []


def get_installed_packages():
    return INSTALLED_PACKAGES


def get_installed_package(name):
    for package in INSTALLED_PACKAGES:
        if package["name"].startswith(name):
            return package
    return None


def load_snippets_and_packages():
    add_action(
        "javatar.util.collection.get_snippet_files", "Load snippets"
    )
    thread = JavatarSnippetsLoaderThread(snippets_complete)
    thread.start()
    ThreadProgress(thread, "Loading Javatar snippets", "Javatar snippets has been loaded")


def snippets_complete(data):
    global SNIPPETS
    SNIPPETS = data
    load_packages()


def load_packages(no_require=False):
    add_action(
        "javatar.util.collection.get_package_files",
        "Load Java default packages"
    )
    thread = JavatarPackagesLoaderThread(packages_complete, no_require)
    thread.start()
    ThreadProgress(thread, "Loading Javatar packages", "Javatar packages has been loaded")


def packages_complete(data, no_require=False):
    global INSTALLED_PACKAGES, DEFAULT_PACKAGES
    INSTALLED_PACKAGES = data["installed_packages"]
    DEFAULT_PACKAGES = data["default_packages"]

    installed_menu = {
        "selected_index": 1,
        "items": [["Back", "Back to previous menu"]],
        "actions": [
            {
                "name": "package_manager"
            }
        ]
    }
    # Installed packages
    install_update = False
    for package in get_installed_packages():
        install_update = True
        installed_menu["actions"].append({"command": "javatar_install", "args": {"installtype": "uninstall_package", "name": package["name"], "filename": package["path"]}})
        installed_menu["items"].append([package["name"], "Installed (" + to_readable_size(package["path"]) + ")."])
    if install_update:
        installed_menu["selected_index"] = 2
        sublime.active_window().run_command("javatar", {"replaceMenu": {
            "name": "uninstall_packages",
            "menu": installed_menu
        }})

    from .javatar_updater import update_packages
    update_packages(no_require)
    from .javatar_utils import stop_clock
    from .javatar_java import detect_jdk
    detect_jdk(on_done=stop_clock)


def get_packages():
    packages = []
    for pck in DEFAULT_PACKAGES:
        packages.append(pck)
    return packages


def get_snippet(name):
    for snippet in SNIPPETS:
        if snippet["class"] == name:
            return snippet["data"]
    return None


def get_snippet_name(index):
    return SNIPPETS[index]["class"]


def get_snippet_list():
    slist = []
    for snippet in SNIPPETS:
        slist.append([snippet["class"], snippet["description"]])
    return slist


def get_dependencies(local=True):
    out_dependencies = []
    if local:
        dependencies = get_project_settings("dependencies")
    else:
        dependencies = get_global_settings("dependencies")
    from os.path import exists
    if dependencies is not None:
        for dependency in dependencies:
            if exists(dependency):
                out_dependencies.append([dependency, local])
    if local:
        for dependency in get_global_settings("dependencies"):
            if exists(dependency):
                out_dependencies.append([dependency, not local])
    return out_dependencies


def refresh_dependencies(local=None):
    if local is None:
        refresh_dependencies(True)
        refresh_dependencies(False)
        return
    dependency_menu = {
        "selected_index": 2,
        "items": [["Back", "Back to previous menu"], ["Add External .jar", "Add dependency .jar file"], ["Add Class Folder", "Add dependency class folder"]],
        "actions": [
            {
                "name": "project_settings"
            }
        ]
    }

    dependency_menu["actions"].append({"command": "javatar_settings", "args": {"actiontype": "add_external_jar", "arg1": local}})
    dependency_menu["actions"].append({"command": "javatar_settings", "args": {"actiontype": "add_class_folder", "arg1": local}})

    dependencies = get_dependencies(local)
    for dependency in dependencies:
        from os.path import isdir
        name = get_path("name", dependency[0])
        if dependency[1]:
            dependency_menu["actions"].append({"command": "javatar_settings", "args": {"actiontype": "remove_dependency", "arg1": dependency[0], "arg2": True}})
            if isdir(dependency[0]):
                dependency_menu["items"].append(["["+name+"]", "Project dependency. Select to remove from the list"])
            else:
                dependency_menu["items"].append([name, "Project dependency. Select to remove from the list"])
        else:
            dependency_menu["actions"].append({"command": "javatar_settings", "args": {"actiontype": "remove_dependency", "arg1": dependency[0], "arg2": False}})
            if isdir(dependency[0]):
                dependency_menu["items"].append(["["+name+"]", "Global dependency. Select to remove from the list"])
            else:
                dependency_menu["items"].append([name, "Global dependency. Select to remove from the list"])
    menu_name = "_dependencies"
    if local:
        menu_name = "local" + menu_name
    else:
        menu_name = "global" + menu_name
    sublime.active_window().run_command("javatar", {"replaceMenu": {
        "name": menu_name,
        "menu": dependency_menu
    }})


class JavatarSnippetsLoaderThread(threading.Thread):
    def __init__(self, on_complete=None):
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def analyse_snippet(self, file):
        add_action(
            "javatar.util.collection.analyse_snippet",
            "Analyse snippet [file="+file+"]"
        )
        data = sublime.load_resource(file)
        classScope = None
        classRe = re.search("%class:(.*)%(\\s*)", data, re.M)
        if classRe is not None:
            classScope = classRe.group(0)
            data = re.sub("%class:(.*)%(\\s*)", "", data)
            classScope = re.sub("(\\s*)$", "", classScope)
            classScope = classScope[7:-1]

        if classScope is None or classScope == "":
            from .javatar_utils import get_path
            classScope = get_path("name", file)[:-8]

        descriptionScope = ""
        descriptionRe = re.search("%description:(.*)%(\\s*)", data, re.M)
        if descriptionRe is not None:
            descriptionScope = descriptionRe.group(0)
            data = re.sub("%description:(.*)%(\\s*)", "", data)
            descriptionScope = re.sub("(\\s*)$", "", descriptionScope)
            descriptionScope = descriptionScope[13:-1]
        return {"file": file, "class": classScope, "description": descriptionScope, "data": data}

    def run(self):
        snippets = []

        from .javatar_utils import get_path
        for filepath in sublime.find_resources("*.javatar"):
            filename = get_path("name", filepath)
            add_action(
                "javatar.util.collection",
                "Javatar snippet " + filename + " loaded"
            )
            print("Javatar snippet " + filename + " loaded")
            snippets.append(self.analyse_snippet(filepath))

        self.result = True
        if self.on_complete is not None:
            sublime.set_timeout(lambda: self.on_complete(snippets), 10)


class JavatarPackagesLoaderThread(threading.Thread):
    def __init__(self, on_complete=None, no_require=False):
        self.installed_packages = []
        self.on_complete = on_complete
        self.no_require = no_require
        threading.Thread.__init__(self)

    def count_classes(self, imports):
        packages = 0
        classes = 0
        if "packages" in imports:
            for packageName in imports["packages"]:
                package = imports["packages"][packageName]
                packages += 1
                if "interface" in package:
                    classes += len(package["interface"])
                if "class" in package:
                    classes += len(package["class"])
                if "enum" in package:
                    classes += len(package["enum"])
                if "exception" in package:
                    classes += len(package["exception"])
                if "error" in package:
                    classes += len(package["error"])
                if "annotation" in package:
                    classes += len(package["annotation"])
                if "type" in package:
                    classes += len(package["type"])
        return [packages, classes]

    def analyse_package(self, filepath):
        add_action(
            "javatar.util.collection.analyse_import",
            "Analyse package [file="+filepath+"]"
        )
        try:
            from .javatar_utils import get_path
            imports = sublime.decode_value(sublime.load_resource(filepath))
            if "experiment" in imports and imports["experiment"]:
                return None
            filename = get_path("name", filepath)
            if "name" in imports:
                filename = imports["name"]
            count = self.count_classes(imports)
            self.installed_packages.append({"name": filename, "path": filepath})
            print("Javatar package \"" + filename + "\" loaded with " + str(count[1]) + " classes in " + str(count[0]) + " packages")
            return imports
        except ValueError:
            sublime.error_message("Invalid JSON format")
        return None

    def run(self):
        default_packages = []
        from .javatar_utils import get_path
        for filepath in sublime.find_resources("*.javatar-packages"):
            filename = get_path("name", filepath)
            add_action(
                "javatar.util.collection",
                "Javatar default package " + filename + " loaded"
            )
            imports = self.analyse_package(filepath)
            if imports is not None:
                default_packages.append(imports)

        data = {
            "installed_packages": self.installed_packages,
            "default_packages": default_packages
        }
        self.result = True
        if self.on_complete is not None:
            sublime.set_timeout(lambda: self.on_complete(data, self.no_require), 10)
