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

        @param window: if provided, will use as a target window,
            otherwise, active window will be used
        """
        window = window or sublime.active_window()
        if window:
            return len(window.folders()) > 0
        return False

    def is_file(self, view=None):
        """
        Returns whether specified view is a file or not

        @param view: if provided, will use as a target view,
            otherwise, active view will be used
        """
        return self.get_file(view) is not None

    def get_file(self, view=None):
        """
        Returns a file within specified view

        @param view: if provided, will use as a target view,
            otherwise, active view will be used
        """
        view = view or sublime.active_window().active_view()
        if view:
            return view.file_name()
        return None

    def get_project_dirs(self, window=None):
        """
        Returns a list of folders opened in the project,
            otherwise, return a list of a current directory

        @param window: if provided, will use as a target window,
            otherwise, active window will be used
        """
        window = window or sublime.active_window()
        if window:
            return window.folders()
        return [self.get_dir()]

    def get_source_folders(self):
        """
        Returns a list of folders which specified as a source folder,
            otherwise, returns a project folders
        """
        return (
            Settings().get("source_folders") or
            self.get_project_dirs()
        )

    def get_root_dir(self):
        """
        Returns a proper root folder in the project

        Root folder will be used to create a new Java file and another tasks
            this should be adapt with current state of the project
        """
        if self.is_project():
            source_folders = self.get_source_folders()
            if source_folders:
                # TODO: Use the one that contains current file
                return source_folders[0]
        if self.get_dir():
            return self.get_dir()
        return None

    def get_dir(self, view=None):
        """
        Returns a directory contains file within specified view

        @param view: if provided, will use as a target view,
            otherwise, active view will be used
        """
        current_file = self.get_file(view)
        if current_file:
            return os.path.dirname(current_file)
        return None


def StateProperty():
    return _StateProperty.instance()
