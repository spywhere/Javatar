import sublime
import sublime_plugin
from ..utils import *


# Multiple source folder


class JavatarSettingsCommand(sublime_plugin.WindowCommand):
    def is_source_folder(self, path, can_empty=True):
        empty = True
        for name in os.listdir(path):
            empty = False
            pathname = os.path.join(path, name)
            if can_empty:
                if os.path.isdir(pathname):
                    if self.is_source_folder(pathname, can_empty):
                        return True
            if os.path.isfile(pathname) and is_java(pathname):
                return True
        return can_empty and empty

    def get_source_folder(self, path):
        folder_list = []
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if os.path.isdir(pathname) and not name.startswith("."):
                folder_list.append([name, pathname])
                folder_list += self.get_source_folder(pathname)
        return folder_list

    def get_folders(self):
        source_folders = [[get_path("name", get_path("project_dir")), get_path("project_dir")+os.sep]]
        source_folders += self.get_source_folder(get_path("project_dir"))
        folders = []
        rootlen = len(get_path("project_dir"))
        for name, folder in source_folders:
            if self.is_source_folder(folder, True):
                folders.append([name, folder[rootlen:]])
        return folders

    def jar_file_filter(self, path):
        return os.path.isdir(path) or path.endswith(".jar")

    def directory_filter(self, path):
        return os.path.isdir(path)

    def file_prelist(self, path):
        dir_list = []
        dir_list.append(["[Current Directory]", path])
        if os.path.dirname(path) != path:
            dir_list.append(["[Parent Folder]", os.path.dirname(path)])
        return dir_list

    def dir_selector(self, path):
        return path.startswith("> ") and path.endswith(" ") and os.path.isdir(path[2:-1])

    def dir_prelist(self, path):
        dir_list = []
        dir_list.append(["[Select This Directory]", "> "+path+" "])
        if os.path.dirname(path) != path:
            dir_list.append(["[Parent Folder]", os.path.dirname(path)])
        return dir_list

    def run(self, actiontype, arg1=None, arg2=None):
        get_action().add_action("javatar.command.project.run", "Project Settings [type="+actiontype+"]")
        self.actiontype = actiontype
        if actiontype == "set_source_folder":
            self.panel_list = self.get_folders()
            if len(self.panel_list) < 1:
                sublime.error_message("No source folder available")
                return
            sublime.active_window().show_quick_panel(self.panel_list, self.on_panel_complete)
        elif actiontype == "add_external_jar":
            self.local = arg1
            fd = JavatarBrowseDialog(initial_dir=parse_macro(get_settings("dependencies_path"), get_macro_data()), path_filter=self.jar_file_filter, on_done=self.on_panel_complete, on_cancel=self.on_panel_cancel)
            fd.browse(prelist=self.file_prelist)
        elif actiontype == "add_class_folder":
            self.local = arg1
            fd = JavatarBrowseDialog(initial_dir=parse_macro(get_settings("dependencies_path"), get_macro_data()), path_filter=self.directory_filter, selector=self.dir_selector, on_done=self.on_panel_complete, on_cancel=self.on_panel_cancel)
            fd.browse(prelist=self.dir_prelist)
        elif actiontype == "remove_dependency":
            self.local = arg2
            if arg2:
                dependencies = get_project_settings("dependencies")
            else:
                dependencies = get_global_settings("dependencies")
            if arg1 in dependencies:
                dependencies.remove(arg1)
            set_settings("dependencies", dependencies, arg2)
            refresh_dependencies()
            menu_name = "_dependencies"
            if self.local:
                menu_name = "local" + menu_name
            else:
                menu_name = "global" + menu_name
            sublime.set_timeout(lambda: sublime.active_window().run_command("javatar", {"action": {"name": menu_name}}), 10)
            sublime.set_timeout(lambda: show_status("Dependency \""+get_path("name", arg1)+"\" has been removed", None, False), 500)
        elif actiontype == "set_jdk":
            self.local = arg1
            detect_jdk(True, self.detect_jdk_complete, True)

    def detect_jdk_complete(self):
        if self.local:
            jdks = JavatarMergedDict(get_global_settings("jdk_version"), get_project_settings("jdk_version"))
        else:
            jdks = JavatarDict(get_global_settings("jdk_version"))
        self.panel_list = []
        self.jdk_list = []
        default_java = get_read_version(get_java_version(check_all=True))
        if default_java is not None:
            self.panel_list.append(["Default JDK", "Default JDK ["+default_java+"]"])
            self.jdk_list.append("")
        if jdks.get_dict():
            for jdk in jdks.get_dict():
                if jdk == "use":
                    continue
                version_name = "JDK " + jdks.get(jdk)["version"]
                if "update" in jdks.get(jdk):
                    version_name += " Update " + jdks.get(jdk)["update"]
                self.panel_list.append([jdk, version_name])
                self.jdk_list.append(jdk)
        if len(self.jdk_list) > 0:
            sublime.active_window().show_quick_panel(self.panel_list, self.on_panel_complete)
        else:
            sublime.error_message("Javatar cannot find JDK installed in your computer.\n\nPlease install or settings the location of installed JDK.")

    def on_panel_cancel(self):
        if self.actiontype == "add_external_jar" or self.actiontype == "add_class_folder":
            menu_name = "_dependencies"
            if self.local:
                menu_name = "local" + menu_name
            else:
                menu_name = "global" + menu_name
            sublime.set_timeout(lambda: sublime.active_window().run_command("javatar", {"action": {"name": menu_name}}), 10)

    def on_panel_complete(self, index):
        if self.actiontype == "set_source_folder":
            source_rel_path = get_path("join", get_path("name", get_path("project_dir")), self.panel_list[index][1][1:])
            set_settings("source_folder", get_path("join", get_path("project_dir"), self.panel_list[index][1][1:]), True)
            sublime.set_timeout(lambda: show_status("Source folder \""+source_rel_path+"\" is set", None, False), 500)
        elif self.actiontype == "set_jdk":
            if self.local:
                jdks = get_project_settings("jdk_version")
            else:
                jdks = get_global_settings("jdk_version")
            if jdks is None:
                jdks = {}
            jdks["use"] = self.jdk_list[index]
            set_settings("jdk_version", jdks, self.local)
            if self.local:
                sublime.set_timeout(lambda: show_status(self.panel_list[index][0] + " has been set for project", None, False), 500)
            else:
                sublime.set_timeout(lambda: show_status(self.panel_list[index][0] + " has been set as default", None, False), 500)
            detect_jdk(True)
        elif self.actiontype == "add_external_jar" or self.actiontype == "add_class_folder":
            if self.actiontype == "add_external_jar":
                path = index
            elif self.actiontype == "add_class_folder":
                path = index[2:-1]
            if self.local:
                dependencies = get_project_settings("dependencies")
            else:
                dependencies = get_global_settings("dependencies")
            if dependencies is None:
                dependencies = []
            dependencies.append(path)
            set_settings("dependencies", dependencies, self.local)
            set_settings("dependencies_path", get_path("parent", path), self.local)
            refresh_dependencies()
            menu_name = "_dependencies"
            if self.local:
                menu_name = "local" + menu_name
            else:
                menu_name = "global" + menu_name
            sublime.set_timeout(lambda: sublime.active_window().run_command("javatar", {"action": {"name": menu_name}}), 10)
            sublime.set_timeout(lambda: show_status("Dependency \""+get_path("name", path)+"\" has been added", None, False), 500)
