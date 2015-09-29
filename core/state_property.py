import sublime
import os
import time
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
        """
        Returns whether specified file or view is a Java file or not

        @param file_path: a target file path
            if provided, will use as a target file path

            otherwise, a file from the active view will be used
        @param view: a target view
            if provided, will use as a target view

            otherwise, active view will be used
        """
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

    def is_source_folder(self, path, can_empty=True):
        """
        Returns whether specified path is a source folder or not

        @param path: a directory path
        @param can_empty: a boolean specified whether the empty folder will
            consider as a source folder
        """
        empty = True
        for name in os.listdir(path):
            empty = False
            path_name = os.path.join(path, name)
            if can_empty:
                if os.path.isdir(path_name):
                    if self.is_source_folder(path_name, can_empty):
                        return True
            if os.path.isfile(path_name) and self.is_java(path_name):
                return True
        return can_empty and empty

    def load_cache(self):
        from .macro import Macro
        from ..utils import Utils
        cache_location = Macro().parse(Settings().get(
            "cache_file_location"
        ))
        cache_path = os.path.join(cache_location, ".javatar-cache")
        if os.path.exists(cache_path):
            cache_file = open(cache_path, "r")
            cache = sublime.decode_value(cache_file.read())
            cache_file.close()
            if "creation_time" in cache:
                valid_time = time.time() - Utils.time_from_string(
                    Settings().get("cache_valid_duration")
                )
                if cache["creation_time"] < valid_time:
                    return {}
            return cache
        else:
            return {}

    def save_cache(self, cache):
        if "creation_time" not in cache:
            cache["creation_time"] = int(time.time())
        from .macro import Macro
        cache_location = Macro().parse(Settings().get(
            "cache_file_location"
        ))
        cache_path = os.path.join(cache_location, ".javatar-cache")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        cache_file = open(cache_path, "w")
        cache_file.write(sublime.encode_value(cache, True))
        cache_file.close()

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

    def get_source_folders(self, file_path=None, as_tuple=False,
                           include_missing=False):
        """
        Returns a list of folders which specified as a source folder,
            otherwise, returns a project folders

        @param file_path: a file path
        @param as_tuple: a boolean specified whether the result will be
            returned as a tuple of (folder path, from global) or not
        @param include_missing: a boolean specified whether returns a list
            with missing source folders or not
        """
        source_folders = [
            source_folder
            for source_folder in Settings().get("source_folders", [])
            if os.path.exists(source_folder) or include_missing
        ]
        if as_tuple:
            if source_folders:
                return (source_folders, True)
            else:
                return (self.get_project_dirs(file_path=file_path), False)
        else:
            return (
                source_folders or
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

    def get_library_paths(self, from_global=False, include_missing=False):
        """
        Returns library path list

        @param from_global: a boolean specified whether returns a library path
            list from global settings or local settings
        @param include_missing: a boolean specified whether returns a list
            with missing library paths or not
        """
        out_library_paths = []
        library_paths = Settings().get(
            "library_paths", from_global=from_global
        )

        if library_paths is not None:
            out_library_paths.extend(
                [library_path, from_global]
                for library_path in library_paths
                if os.path.exists(library_path) or include_missing
            )

        if not from_global:
            out_library_paths.extend(
                [library_path, True]
                for library_path in Settings().get(
                    "library_paths", default=[], from_global=True
                )
                if os.path.exists(library_path) or include_missing
            )

        return out_library_paths

    def refresh_library_paths(self, from_global=None):
        if from_global is None:
            self.refresh_library_paths(True)
            self.refresh_library_paths(False)
            return
        previous_menu = "global_settings" if from_global else "project_settings"
        library_paths_menu = {
            "selected_index": 2,
            "items": [
                [
                    "Back",
                    "Back to previous menu"
                ], [
                    "Add Library Path",
                    "Add a library path to be used when run the program"
                ],
            ],
            "actions": [
                {
                    "name": previous_menu
                }, {
                    "command": "javatar_project_settings",
                    "args": {
                        "action_type": "add_library_path",
                        "to_global": from_global
                    }
                }
            ]
        }

        library_paths = self.get_library_paths(from_global, True)
        for library_path in library_paths:
            name = os.path.basename(library_path[0])
            if library_path[1]:
                library_paths_menu["actions"].append(
                    {
                        "command": "javatar_project_settings",
                        "args": {
                            "action_type": "remove_library_path",
                            "library_path": library_path[0],
                            "from_global": True
                        }
                    }
                )
                if not os.path.exists(library_path[0]):
                    library_paths_menu["items"].append([
                        "[Missing] " + name,
                        "Global library path. Select to remove from the list"
                    ])
                elif os.path.isdir(library_path[0]):
                    library_paths_menu["items"].append([
                        "[" + name + "]",
                        "Global library path. Select to remove from the list"
                    ])
                else:
                    library_paths_menu["items"].append([
                        name,
                        "Global library path. Select to remove from the list"
                    ])
            else:
                library_paths_menu["actions"].append(
                    {
                        "command": "javatar_project_settings",
                        "args": {
                            "action_type": "remove_library_path",
                            "library_path": library_path[0],
                            "from_global": False
                        }
                    }
                )
                if not os.path.exists(library_path[0]):
                    library_paths_menu["items"].append([
                        "[Missing] " + name,
                        "Project library path. Select to remove from the list"
                    ])
                elif os.path.isdir(library_path[0]):
                    library_paths_menu["items"].append([
                        "[" + name + "]",
                        "Project library path. Select to remove from the list"
                    ])
                else:
                    library_paths_menu["items"].append([
                        name,
                        "Project library path. Select to remove from the list"
                    ])

        menu_name = "_library_paths"
        if from_global:
            menu_name = "global" + menu_name
        else:
            menu_name = "local" + menu_name
        sublime.active_window().run_command("javatar", {"replaceMenu": {
            "name": menu_name,
            "menu": library_paths_menu
        }})

    def refresh_source_folders(self):
        """
        Refresh the source folders menu
        """
        source_folder_menu = {
            "selected_index": 2,
            "items": [
                [
                    "Back",
                    "Back to previous menu"
                ], [
                    "Add Source Folder",
                    "Add a source folder to specified as default package"
                ]
            ],
            "actions": [
                {
                    "name": "project_settings"
                }, {
                    "command": "javatar_project_settings",
                    "args": {
                        "action_type": "add_source_folder"
                    }
                }
            ]
        }

        source_folders, from_settings = self.get_source_folders(
            as_tuple=True, include_missing=True
        )
        for source_folder in source_folders:
            name = os.path.basename(source_folder)
            source_folder_menu["actions"].append({
                "command": "javatar_project_settings",
                "args": {
                    "action_type": "remove_source_folder",
                    "source_folder": source_folder
                }
            })
            source_folder_menu["items"].append([
                (
                    "[Missing] " if not os.path.exists(source_folder) else ""
                ) + name,
                (
                    "Select to remove from the list"
                    if from_settings
                    else "Default source folder." +
                    " Add a new one to override this folder"
                )
            ])
        sublime.active_window().run_command("javatar", {"replaceMenu": {
            "name": "local_source_folders",
            "menu": source_folder_menu
        }})


def StateProperty():
    return _StateProperty.instance()
