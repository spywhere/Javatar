from os import pathsep, makedirs
from os.path import isdir

import sublime
import sublime_plugin
from time import clock, sleep
from ..utils import *


# Create .jar using "jar" command
# http://docs.oracle.com/javase/7/docs/technotes/tools/windows/jar.html


class JavatarBuildCommand(sublime_plugin.WindowCommand):
    build_list = []
    build_size = -1
    failed = False
    view = None

    def build(self):
        self.start_time = clock()
        self.view = None
        self.failed = False
        self.build_size = len(self.build_list)
        self.progress = MultiThreadProgress("Preparing build", None, self.on_build_thread_complete, self.on_all_complete)
        num_thread = 1

        self.source_folder = get_path("source_folder")
        self.build_output_location = get_settings("build_output_location")
        self.build_command = get_settings("build_command")
        self.build_location = get_settings("build_location")

        if get_settings("parallel_build") > num_thread:
            num_thread = get_settings("parallel_build")
        for i in range(num_thread):
            self.on_build_thread_complete(None)

    def on_build_thread_complete(self, thread):
        if self.build_size <= 0:
            return
        if self.build_size > 0 and self.view is not None and self.view.window() is None:
            self.build_size = -1
            return
        if len(self.build_list) > 0:
            file_path = self.build_list[0]
            del self.build_list[0]
            build = self.create_build(file_path)
            if build is None:
                return
            self.progress.add(build, get_path("name", file_path))
            if not self.progress.running:
                self.progress.run()
            if self.view is not None:
                self.view.set_name(self.progress.get_message())
        self.progress.set_message("[" + str(self.build_size - len(self.build_list)) + "/" + str(self.build_size) + "] Building ")

    def create_build(self, file_path):
        self.macro_data["sourcepath"] = "-sourcepath \"" + self.source_folder + "\""
        dependencies = get_dependencies()
        dependencies_param = ""
        for dependency in dependencies:
            if dependencies_param == "":
                dependencies_param = "-classpath ." + pathsep + "\"" + dependency[0] + "\""
            else:
                dependencies_param += pathsep + "\"" + dependency[0] + "\""
        self.macro_data["classpath"] = dependencies_param
        self.macro_data["d"] = ""
        if self.build_output_location != "":
            output_dir = parse_macro(self.build_output_location, self.macro_data, file_path)
            if not isdir(output_dir):
                makedirs(output_dir)
            self.macro_data["d"] = "-d \"" + output_dir + "\""
        executable = get_executable("build")
        if executable is None:
            return None
        build_script = parse_macro(self.build_command, self.macro_data, file_path)
        shell = JavatarSilentShell(executable + " " + build_script, self.on_build_done)
        shell.set_cwd(parse_macro(self.build_location, self.macro_data))
        shell.start()
        return shell

    def on_build_done(self, elapse_time, data, return_code, params):
        if self.build_size > 0 and self.view is not None and self.view.window() is None:
            self.build_size = -1
            return
        if data is not None:
            if self.view is None:
                self.view = self.window.new_file()
                self.failed = True
                self.view.set_name("Preparing build log...")
                self.view.set_syntax_file("Packages/Javatar/syntax/JavaCompilationError.tmLanguage")
                # Prevent view access while creating which cause double view to create
                sleep(get_settings("build_log_delay"))
            self.view.set_scratch(True)
            self.view.run_command("javatar_util", {"util_type": "add", "text": data})

    def on_all_complete(self):
        if self.build_size < 0:
            show_notification("Building Cancelled")
            sublime.status_message("Building Cancelled")
            add_action(
                "javatar.command.build.complete", "Building Cancelled"
            )
            return

        message = "Building Finished [{0:.2f}s]"
        if self.failed:
            message = "Building Failed [{0:.2f}s]"

        show_notification(message.format(clock() - self.start_time))
        self.build_size = -1
        if self.view is not None:
            self.view.set_name(message.format(clock() - self.start_time))
        sublime.status_message(message.format(clock() - self.start_time))
        add_action(
            "javatar.command.build.complete",
            message.format(clock() - self.start_time)
        )

    def get_java_files(self, dir_path):
        for name in os.listdir(dir_path):
            pathname = os.path.join(dir_path, name)
            if os.path.isdir(pathname) and name not in get_sublime_settings("folder_exclude_patterns", []):
                self.get_java_files(pathname)
            elif os.path.isfile(pathname) and is_java(pathname):
                self.build_list.append(pathname)

    def build_all(self, dir_path):
        self.get_java_files(dir_path)
        if len(self.build_list) > 0:
            add_action(
                "javatar.command.build.build_all", "Build all"
            )
            self.build()
            return True
        else:
            return False

    def run(self, build_type=""):
        self.macro_data = get_macro_data()
        self.build_list = []
        add_action(
            "javatar.command.build.run",
            "Build [build_type=" + build_type + "]"
        )
        view = sublime.active_window().active_view()
        if build_type == "project":
            if is_project():
                for view in self.window.views():
                    if is_java(view.file_name()):
                        if view.is_dirty():
                            if get_settings("automatic_save"):
                                self.window.run_command("save_all")
                            else:
                                sublime.error_message("Some Java files are not saved")
                                return
                if not self.build_all(get_package_root_dir()):
                    sublime.error_message("No class to build")
            else:
                sublime.error_message("Unknown package location")
        elif build_type == "package":
            if is_project():
                for view in self.window.views():
                    if is_java(view.file_name()):
                        if view.is_dirty():
                            if get_settings("automatic_save"):
                                self.window.run_command("save_all")
                            else:
                                sublime.error_message("Some Java files are not saved")
                                return
                if not self.build_all(get_path("current_dir")):
                    sublime.error_message("No class to build")
            else:
                sublime.error_message("Unknown package location")
        elif build_type == "working":
            if is_project():
                for view in self.window.views():
                    if is_java(view.file_name()):
                        self.build_list.append(view.file_name())
                        if view.is_dirty():
                            if get_settings("automatic_save"):
                                self.window.run_command("save_all")
                            else:
                                sublime.error_message("Some Java files are not saved")
                                return
                if len(self.build_list) > 0:
                    add_action(
                        "javatar.command.build.build_working",
                        "Build working files"
                    )
                    self.build()
                else:
                    sublime.error_message("No class to build")
            else:
                sublime.error_message("Unknown package location")
        elif build_type == "class":
            if is_project() and is_file():
                if is_java(view.file_name()):
                    if self.window.active_view().is_dirty():
                        if get_settings("automatic_save"):
                            self.window.run_command("save")
                        else:
                            sublime.error_message("Current file is not saved")
                            return
                    add_action(
                        "javatar.command.build.build_file", "Build file"
                    )
                    self.build_list.append(view.file_name())
                    self.build()
                else:
                    sublime.error_message("Current file is not Java")
            else:
                sublime.error_message("Unknown class location")
