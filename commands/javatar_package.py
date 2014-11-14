import sublime
import sublime_plugin
import os
import shlex
import shutil
import hashlib
from ..utils import *


class JavatarCreateJavatarPackageCommand(sublime_plugin.WindowCommand):
    package_step = None
    package_info = []

    def write_output(self, text):
        view = self.window.new_file()
        view.set_name("Javatar Packages wizard report")
        view.set_scratch(True)
        view.run_command("javatar_util", {"util_type": "add", "text": text, "dest": "Javatar Packages wizard report"})
        view.run_command("javatar_util", {"util_type": "set_read_only"})

    def on_complete(self):
        output = "## Javatar Packages report\n"
        output += "* Package name: " + self.package_info[0] + "\n"
        output += "* Package filename: " + self.package_info[1] + "\n"
        if self.package_info[2] != "":
            output += "* Package conflicts: " + self.package_info[2] + "\n"
        search_path = get_path("parent", get_path("project_dir"))
        doclet_path = None
        for name in os.listdir(search_path):
            pathname = os.path.join(search_path, name)
            if os.path.isdir(pathname) and self.is_doclet_folder(pathname):
                doclet_path = pathname
                break
        if doclet_path is None:
            sublime.error_message("Javatar doclet not found")
            return

        output += "## Generated Packages\n"
        # make sure that run in correct directory
        command = "cd " + shlex.quote(search_path) + ";"
        command += "echo Generating...;"
        command += "javadoc -sourcepath " + shlex.quote(os.path.join(get_path("source_folder"), self.package_info[3][1][1:])) + " -docletpath " + shlex.quote(doclet_path) + " -name " + shlex.quote(self.package_info[0]) + " -doclet me.spywhere.doclet.Javatar -quiet "

        rootlen = len(os.path.join(get_path("project_dir"), self.package_info[3][1][1:]))
        package_dirs = self.get_source_folder(os.path.join(get_path("project_dir"), self.package_info[3][1][1:]))
        for package_dir in package_dirs:
            if self.is_source_folder(package_dir[1], False):
                package = to_package(package_dir[1][rootlen:], False)
                output += "* " + package + "\n"
                command += " " + package

        command += ";echo Done"

        output += "\n## Package Info\n"
        output += "\n*Output file: " + os.path.join(search_path, self.package_info[1]) + ".javatar-packages\n"

        sublime.active_window().run_command("exec", {"shell_cmd": command})

        self.finalize_package(output, os.path.join(search_path, self.package_info[0]), os.path.join(search_path, self.package_info[1]))

    def finalize_package(self, output, path, path2, time=0):
        # should not exceed 10 seconds
        if not os.path.exists(path+".json"):
            if time < get_settings("maximum_waiting_time"):
                sublime.set_timeout(lambda: self.finalize_package(output, path, path2, time+1), 1000)
            else:
                sublime.message_dialog("Package creation taking too long...")
            return
        shutil.move(path+".json", path2+".javatar-packages")

        datafile = open(path2+".javatar-packages", "r")
        data = datafile.read()
        datafile.close()
        datahash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        output += "*Hash Checksum: " + datahash + "\n"
        output += "*File Size: " + to_readable_size(path2+".javatar-packages") + "\n"

        # Print sample code

        self.write_output(output)

    def is_doclet_folder(self, path, level=0):
        class_path = ["me", "spywhere", "doclet"]
        if level >= len(class_path):
            return True
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if os.path.isdir(pathname) and name == class_path[level]:
                return self.is_doclet_folder(pathname, level+1)
        return False

    def get_filename(self):
        '''
        Convert filename by...
            - Preserve first word
            - Remove all spaces and underscores
            - Remove all remaining word's lowercase
            - If number is version (followed by .) and prefixed or suffixed by space, change space to dash
        * Invalid filename is not validated

        Example:
            Java Standard Edition 8 -> JavaSE8
            Bukkit 1.7.2 R0.3 Beta Build -> Bukkit-1.7.2-R0.3-BB
        '''
        filename = ""
        infilename = self.package_info[0]
        wordstart = False
        worddone = False
        justspace = False
        justnumber = False
        index = -1
        for char in infilename:
            index += 1
            if char == ' ' or char == '_':
                if justnumber:
                    filename += '-'
                justspace = True
                if wordstart:
                    worddone = True
                continue
            if worddone and char >= 'a' and char <= 'z':
                continue
            if char >= '0' and char <= '9':
                justnumber = True
                if justspace and index+1 < len(infilename) and infilename[index+1] == '.':
                    filename += '-'
            else:
                justnumber = False
            filename += char
            wordstart = True
            justspace = False
        return filename

    def is_source_folder(self, path, can_empty=True):
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if can_empty:
                if os.path.isdir(pathname):
                    if self.is_source_folder(pathname):
                        return True
            if os.path.isfile(pathname) and is_java(pathname):
                return True
        return False

    def get_source_folder(self, path):
        folder_list = []
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if os.path.isdir(pathname) and not name.startswith("."):
                folder_list.append([name, pathname])
                folder_list += self.get_source_folder(pathname)
        return folder_list

    def get_folders(self):
        source_folders = [[get_path("name", get_path("project_dir")), get_path("project_dir")+"/"]]
        source_folders += self.get_source_folder(get_path("project_dir"))
        folders = []
        rootlen = len(get_path("project_dir"))
        for name, folder in source_folders:
            if self.is_source_folder(folder):
                folders.append([name, folder[rootlen:]])
        return folders

    def run(self, first=True, again=False):
        if first:
            self.package_info = []
            add_action(
                "javatar.command.package.create_javatar_package.run",
                "Create Javatar Package"
            )
        if self.package_step is None:
            self.package_step = [
                {"input": "Package Name", "flags": "not empty", "message": "Welcome to Javatar Packages wizard\n   This wizard will helps you through package creation and automated some tasks for you.\n   First, you must ensure that you already place \"JavatarDoclet\" in " + get_path("parent", get_package_root_dir()) + "\n\nWizard will ask you for the following infomations...\n - Package name: This will be your package name which appear on installation\n - Preferred file name: This will be your package file name that will be created and uploaded to packages channel\n - Conflicted packages: This informations help users install your package without conflicting another package\n - Source folder: You will be asked for source folder to generate a proper .javatar-packages file\n\nTo cancel, dismiss this dialog and press \"Escape\" key"},
                {"input": "Preferred File Name", "from": self.get_filename},
                {"input": "Conflict Packages starts with", "initial": "Package1,Package2,Package3"},
                {"quick_panel": self.get_folders, "on_error": "No source folder can be use", "message": "Select source folder"}
            ]
        if len(self.package_info) >= len(self.package_step):
            self.on_complete()
            return
        self.current_step = self.package_step[len(self.package_info)]
        if not again and "message" in self.current_step:
            sublime.message_dialog(self.current_step["message"])
        if "input" in self.current_step:
            initial = ""
            if "initial" in self.current_step:
                initial = self.current_step["initial"]
            if "from" in self.current_step:
                initial = self.current_step["from"]()
            sublime.active_window().show_input_panel(self.current_step["input"] + ":", initial, self.on_input_complete, "", "")
        elif "quick_panel" in self.current_step:
            self.panel_list = self.current_step["quick_panel"]()
            if len(self.panel_list) < 1:
                if "on_error" in self.current_step:
                    sublime.error_message(self.current_step["on_error"])
            else:
                sublime.active_window().show_quick_panel(self.panel_list, self.on_panel_complete)

    def on_input_complete(self, text):
        if "flags" in self.current_step:
            if self.current_step["flags"] == "not empty" and text == "":
                sublime.error_message(self.current_step["input"] + " must not empty")
                self.run(False, True)
                return
        self.package_info.append(text)
        self.run(False)

    def on_panel_complete(self, index):
        self.package_info.append(self.panel_list[index])
        self.run(False)


class JavatarCreatePackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.showInput()

    def showInput(self):
        sublime.active_window().show_input_panel("Package Name:", "", self.createPackage, self.on_change, self.on_cancel)

    def on_change(self, text):
        show_status(self.createPackage(text, True), delay=-1, require_java=False)

    def on_cancel(self):
        hide_status(clear=True)

    def createPackage(self, text, on_change=False):
        add_action(
            "javatar.command.package.create_package",
            "Create package [package="+text+"]"
        )
        relative = True
        if text.startswith("~"):
            text = text[1:]
            relative = False

        if not is_project() and not (is_project() and is_file()):
            if on_change:
                return "Cannot specify package location"
            sublime.error_message("Cannot specify package location")
            return
        if not is_package(text):
            if on_change:
                return "Invalid package naming"
            sublime.error_message("Invalid package naming")
            return
        if relative and get_path("current_dir") is not None:
            create_directory = get_path("join", get_path("current_dir"), package_as_directory(text))
        else:
            create_directory = get_path("join", get_package_root_dir(), package_as_directory(text))
        package = to_package(get_path("relative", create_directory, get_package_root_dir()), False)
        if on_change:
            return "Package \""+package+"\" will be created"
        make_package(create_directory)
        show_status("Package \""+package+"\" is created", None, False)
