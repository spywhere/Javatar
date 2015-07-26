import sublime
import sublime_plugin
from ...core import (
    BuildSystem,
    JavaUtils,
    Settings,
    StateProperty
)


class JavatarBuildCommand(sublime_plugin.WindowCommand):

    """
    A command to build a project
    """

    def build_project(self):
        """
        Build a project

        This will build all source code files in all source folders
        """
        if not StateProperty().is_project():
            sublime.error_message("Unknown package location")
            return
        for view in self.window.views():
            if JavaUtils().is_java(view) and view.is_dirty():
                if Settings().get("automatic_save"):
                    self.window.run_command("save_all")
                    break
                else:
                    sublime.error_message("Some Java files are not saved")
                    return
        error_message = BuildSystem().build_dirs(
            StateProperty().get_source_folders(),
            window=self.window
        )
        if error_message:
            sublime.error_message(error_message)

    def build_package(self):
        """
        Build files in the same package

        This will build all source code files in the same package as
            current file
        """
        if not StateProperty().is_project() or not StateProperty().get_dir():
            sublime.error_message("Unknown package location")
            return
        for view in self.window.views():
            if JavaUtils().is_java(view) and view.is_dirty():
                if Settings().get("automatic_save"):
                    self.window.run_command("save_all")
                    break
                else:
                    sublime.error_message("Some Java files are not saved")
                    return
        error_message = BuildSystem().build_dir(
            StateProperty().get_dir(),
            window=self.window
        )
        if error_message:
            sublime.error_message(error_message)

    def build_working(self):
        """
        Build opened files

        This will build all source code files opened in the window
        """
        if not StateProperty().is_project():
            sublime.error_message("Unknown package location")
            return
        files = []
        for view in self.window.views():
            if view.file_name() and JavaUtils().is_java(view):
                files.append(view.file_name())
            if JavaUtils().is_java(view) and view.is_dirty():
                if Settings().get("automatic_save"):
                    self.window.run_command("save_all")
                else:
                    sublime.error_message("Some Java files are not saved")
                    return
        error_message = BuildSystem().build_files(files, window=self.window)
        if error_message:
            sublime.error_message(error_message)

    def build_class(self):
        """
        Build current file

        This will build only currently opened source code file
        """
        view = self.window.active_view()
        if (not StateProperty().is_project() or
                not StateProperty().is_file(view)):
            sublime.error_message("Unknown package location")
            return
        if not JavaUtils().is_java(view):
            sublime.error_message("Current file is not Java")
            return
        if view.is_dirty():
            if Settings().get("automatic_save"):
                self.window.run_command("save_all")
            else:
                sublime.error_message("Some Java files are not saved")
                return
        error_message = BuildSystem().build_files(
            [view.file_name()],
            window=self.window
        )
        if error_message:
            sublime.error_message(error_message)

    def run(self, build_type=None):
        """
        Run the build command
        """
        if not build_type:
            return
        if build_type == "project":
            self.build_project()
        elif build_type == "package":
            self.build_package()
        elif build_type == "working":
            self.build_working()
        elif build_type == "class":
            self.build_class()
