import sublime
import os.path
from .settings import Settings


class _StateProperty:

    """
    Editor state such as projects, working files and related properties
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def is_project(self, window=None):
        """
        Returns whether specified window is a project or not

        @param window: a target window
            if provided, will use as a target window

            otherwise, active window will be used
        """
        window = window or sublime.active_window()
        if window:
            return len(window.folders()) > 0
        return False

    def is_file(self, view=None):
        """
        Returns whether specified view is a file or not

        @param view: a target view
            if provided, will use as a target view

            otherwise, active view will be used
        """
        return self.get_file(view) is not None

    def is_java(self, file_path=None, view=None):
        if not file_path and not view:
            view = sublime.active_window().active_view()
            if view.file_name():
                return (
                    self.is_file(view) and
                    self.is_java(file_path=view.file_name())
                )
        elif file_path:
            _, ext = os.path.splitext(os.path.basename(file_path))
            return ext in Settings().get("java_extensions")
        return (
            view and
            view.find_by_selector(Settings().get("java_source_selector"))
        )

    def get_file(self, view=None):
        """
        Returns a file within specified view

        @param view: a target view used as a target view,
            otherwise, active view will be used
        """
        view = view or sublime.active_window().active_view()
        if view:
            return view.file_name()
        return None

    def get_project_dirs(self, window=None, file_path=None):
        """
        Returns a list of folders opened in the project,
            otherwise, return a list of a current directory

        @param window: a target window used as a target window,
            otherwise, active window will be used
        @param file_path: a file path
        """
        window = window or sublime.active_window()
        if window:
            return window.folders()
        return [self.get_dir(file_path=file_path)]

    def get_source_folders(self, file_path=None):
        """
        Returns a list of folders which specified as a source folder,
            otherwise, returns a project folders

        @param file_path: a file path
        """
        return (
            Settings().get("source_folders") or
            self.get_project_dirs(file_path=file_path)
        )

    def get_source_folder(self, file_path=None):
        """
        Returns a source folder contains a specified file

        Source folder will be used to create a new Java file and another tasks
            this should be adapt with current state of the project

        @param file_path: a file path
        """
        file_path = file_path or self.get_file()
        from ..utils import Utils
        if self.is_project():
            source_folders = self.get_source_folders(file_path=file_path)
            if source_folders:
                if not file_path:
                    return source_folders[0]
                for source_folder in source_folders:
                    if Utils.contains_file(source_folder, file_path):
                        return source_folder
        if self.get_dir(file_path=file_path):
            return self.get_dir(file_path=file_path)
        return None

    def get_root_dir(self, file_path=None, view=None):
        """
        Returns a proper root folder in the project

        Root folder will be used to run a project and use for another tasks
            this should be adapt with current state of the project

        @param file_path: a file path
        @param view: a target view used as a target view,
            otherwise, active view will be used
        """
        if self.is_project():
            project_folders = self.get_project_dirs(file_path=file_path)
            if project_folders:
                return project_folders[0]
        if self.get_dir():
            return self.get_dir(file_path=file_path, view=view)
        return None

    def get_dir(self, file_path=None, view=None):
        """
        Returns a directory contains a file in a specified view if not a
            specified file path

        @param file_path: a file path
        @param view: a target view used as a target view,
            otherwise, active view will be used
        """
        file_path = file_path or self.get_file(view)
        if file_path:
            return os.path.dirname(file_path)
        return None


def StateProperty():
    return _StateProperty.instance()
