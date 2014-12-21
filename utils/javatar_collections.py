from os.path import isdir, exists, basename

import re
import sublime
import threading
from .javatar_actions import add_action
from .javatar_thread import ThreadProgress
from .javatar_utils import to_readable_size, get_project_settings, get_global_settings


INSTALLED_PACKAGES = []
SNIPPETS = []
DEFAULT_PACKAGES = []


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
    return [
        [snippet["class"], snippet["description"]]
        for snippet in SNIPPETS
    ]


def get_dependencies(local=True):
    out_dependencies = []
    if local:
        dependencies = get_project_settings("dependencies")
    else:
        dependencies = get_global_settings("dependencies")

    if dependencies is not None:
        out_dependencies.extend(
            [dependency, local]
            for dependency in dependencies
            if exists(dependency)
        )

    if local:
        out_dependencies.extend(
            [dependency, not local]
            for dependency in get_global_settings("dependencies")
            if exists(dependency)
        )

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

    dependency_menu["actions"].extend([
        {"command": "javatar_settings", "args": {"actiontype": "add_external_jar", "arg1": local}},
        {"command": "javatar_settings", "args": {"actiontype": "add_class_folder", "arg1": local}}
    ])

    dependencies = get_dependencies(local)
    for dependency in dependencies:
        name = basename(dependency[0])
        if dependency[1]:
            dependency_menu["actions"].append({"command": "javatar_settings", "args": {"actiontype": "remove_dependency", "arg1": dependency[0], "arg2": True}})
            if isdir(dependency[0]):
                dependency_menu["items"].append(["[" + name + "]", "Project dependency. Select to remove from the list"])
            else:
                dependency_menu["items"].append([name, "Project dependency. Select to remove from the list"])
        else:
            dependency_menu["actions"].append({"command": "javatar_settings", "args": {"actiontype": "remove_dependency", "arg1": dependency[0], "arg2": False}})
            if isdir(dependency[0]):
                dependency_menu["items"].append(["[" + name + "]", "Global dependency. Select to remove from the list"])
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

    def analyse_snippet(self, filename):
        add_action(
            "javatar.util.collection.analyse_snippet",
            "Analyse snippet [file=" + filename + "]"
        )
        data = sublime.load_resource(filename)

        attrs = {}

        def callback(m):
            key, val = m.groups()

            if key == 'class':
                attrs['classScope'] = val

            elif key == 'description':
                attrs['descriptionScope'] = val

        data = re.sub(r'%(description|class):([^%]+)%\n', callback, data)

        return {
            "file": filename,
            "class": attrs['classScope'],
            "description": attrs['descriptionScope'],
            "data": data
        }

    def run(self):
        snippets = []

        for filepath in sublime.find_resources("*.javatar"):
            filename = basename(filepath)
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

        keys = {
            "interface",
            "class",
            "enum",
            "exception",
            "error",
            "annotation",
            "type"
        }

        if "packages" in imports:
            for packageName in imports["packages"]:
                package = imports["packages"][packageName]
                packages += 1

                for key in keys:
                    if key in package:
                        classes += len(package[key])

        return [packages, classes]

    def analyse_package(self, filepath):
        add_action(
            "javatar.util.collection.analyse_import",
            "Analyse package [file=" + filepath + "]"
        )

        try:
            imports = sublime.decode_value(sublime.load_resource(filepath))

        except ValueError:
            sublime.error_message("Invalid JSON format")

        else:
            if "experiment" in imports and imports["experiment"]:
                return None
            filename = basename(filepath)
            if "name" in imports:
                filename = imports["name"]
            count = self.count_classes(imports)
            self.installed_packages.append({"name": filename, "path": filepath})
            print(
                'Javatar package "{}" loaded with {} classes in {} packages'
                .format(
                    filename,
                    count[1],
                    count[0]
                )
            )
            return imports

        return None

    def run(self):
        default_packages = []
        for filepath in sublime.find_resources("*.javatar-packages"):
            filename = basename(filepath)
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
