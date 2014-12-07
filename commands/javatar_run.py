from os import pathsep
from os.path import join, exists, relpath

import sublime
import sublime_plugin
from ..utils import (
    is_project,
    is_file,
    get_settings,
    parse_macro,
    get_macro_data,
    without_extension,
    get_package_root_dir,
    add_action,
    get_main_class_name,
    get_dependencies,
    get_executable,
    JavatarShell,
    ThreadProgress,
    get_source_folder,
    get_target_view_index
)


class JavatarRunMainCommand(sublime_plugin.WindowCommand):
    def run(self):
        if is_project():
            if is_file():
                found_main = False
                view = sublime.active_window().active_view()
                self.output_dir = get_source_folder()
                if get_settings("build_output_location") != "":
                    self.output_dir = parse_macro(get_settings("build_output_location"), get_macro_data(), view.file_name())
                method_regions = view.find_by_selector("entity.name.function.java")
                for region in method_regions:
                    if view.substr(region) == "main":
                        found_main = True
                        break
                if found_main:
                    file_path = without_extension(relpath(view.file_name(), get_package_root_dir())) + ".class"
                    if not exists(join(self.output_dir, file_path)):
                        sublime.error_message("File is not compiled")
                        return
                    self.on_run()
                else:
                    sublime.error_message("Current file is not main class")
            else:
                sublime.error_message("Unknown class location")
        else:
            sublime.error_message("Unknown package location")

    def on_run(self):
        add_action("javatar.command.run.on_run", "Run main class")
        view = sublime.active_window().active_view()
        file_path = view.file_name()
        self.class_name = get_main_class_name(file_path, view)
        macro_data = get_macro_data(self.class_name)
        dependencies = get_dependencies()
        dependencies_param = "-classpath \"" + self.output_dir + "\""
        for dependency in dependencies:
            dependencies_param += pathsep + "\"" + dependency[0] + "\""
        macro_data["classpath"] = dependencies_param
        macro_data["program_arguments"] = get_settings("program_arguments")
        executable = get_executable("run")
        if executable is None:
            return None
        run_script = parse_macro(get_settings("run_command"), macro_data, file_path)
        target_group, target_index = get_target_view_index("output_console_target_group")
        self.view = self.window.new_file()
        self.window.set_view_index(self.view, target_group, target_index)
        self.view.set_syntax_file("Packages/Javatar/syntax/JavaStackTrace.tmLanguage")
        self.view.set_name("Running " + self.class_name + " ...")
        self.view.set_scratch(True)
        shell = JavatarShell(executable + " " + run_script, self.view, self.on_complete)
        shell.set_cwd(parse_macro(get_settings("run_location"), macro_data))
        shell.start()
        ThreadProgress(shell, "Running Javatar Shell", "Javatar Shell has been stopped")

    def on_complete(self, elapse_time, return_code, params):
        if return_code is not None:
            self.view.set_name(self.class_name + " Ended (Return: " + str(return_code) + ") [{0:.2f}s]".format(elapse_time))
