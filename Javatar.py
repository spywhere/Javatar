import os
import sublime
import sublime_plugin


STATUS = "Javatar"


class JavatarCallCommand(sublime_plugin.TextCommand):
    def run(self, edit, type=""):
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
            else:
                self.view.insert(edit, sel.a, "Javatar Call")
        # Show command dialog for returning a package name or anything related


class CreatePackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = self.window.show_input_panel("Package Name:", "", self.createPackage, "", "")
        view.set_name("JavatarCreatePackage")

    def createPackage(self, text):
        current_dir = getPath("project_dir")
        package_dir = text.split(".")
        package_dir.insert(0, current_dir)
        target_dir = "/".join(package_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        showStatus("Package \""+toPackage(target_dir)+"\" is created")
        # self.window.active_view().set_status(STATUS, )
        self.clear()


class CreateSubpackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        view = self.window.show_input_panel("Subpackage Name:", "", self.createSubpackage, "", "")
        view.set_name("JavatarCreateSubpackage")

    def createSubpackage(self, text):
        current_dir = getPath("current_dir")
        package_dir = text.split(".")
        package_dir.insert(0, current_dir)
        target_dir = "/".join(package_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        showStatus("Subpackage \""+toPackage(target_dir)+"\" is created")
        self.clear()


class CreateClassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Class")


class CreateInterfaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Interface")


class CreateEnumCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Enum")


class BuildProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Build Project")


class CreateJarFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create JAR File")


class CreateExeJarFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Executable JAR File")


def showStatus(text, delay=5000):
    view = sublime.active_window().active_view()
    view.set_status(STATUS, text)
    sublime.set_timeout(hideStatus, delay)


def hideStatus():
    view = sublime.active_window().active_view()
    view.erase_status(STATUS)


def toPackage(dir):
    dir = os.path.relpath(dir, getPath("project_dir"))
    package = ".".join(dir.split("/"))
    if package.startswith("."):
        package = package[1:]
    return package


def getPath(type="", dir=""):
    window = sublime.active_window()
    if type == "project_dir":
        project_data = window.project_data()
        folder_entries = []
        folders = ""
        if project_data is not None:
            folder_entries = project_data.get("folders", [])
        for index in range(len(folder_entries)):
            folder_entry = folder_entries[index]
            if "path" in folder_entry:
                return folder_entry["path"]
        return folders
    elif type == "current_dir":
        return getPath("parent", getPath("current_file"))
    elif type == "current_file":
        return window.active_view().file_name()
    elif type == "parent":
        return os.path.dirname(dir)
    elif type == "name":
        return os.path.basename(dir)
    else:
        return ""
