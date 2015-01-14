import sublime
from os.path import basename, isdir, exists
from .settings import Settings


class DependencyManager:

    """
    Load and store all dependencies
    """

    @staticmethod
    def startup():
        """
        Refresh dependencies list after start up
        """
        DependencyManager.refresh_dependencies()

    @staticmethod
    def get_dependencies(from_global=True):
        """
        Returns dependency list

        @param from_global: if provided as True, will returns a dependency
            list from global settings
        """
        out_dependencies = []
        dependencies = Settings.get("dependencies", from_global=from_global)

        if dependencies is not None:
            out_dependencies.extend(
                [dependency, from_global]
                for dependency in dependencies
                if exists(dependency)
            )

        if not from_global:
            out_dependencies.extend(
                [dependency, True]
                for dependency in Settings.get("dependencies", from_global=True)
                if exists(dependency)
            )

        return out_dependencies

    @staticmethod
    def refresh_dependencies(from_global=None):
        """
        Refresh dependency list

        @param from_global: if provided as None, will refresh all dependencies
            if provided as True, will refresh only global dependencies settings
            if provided as False, will refresh only local dependencies settings
        """
        if from_global is None:
            DependencyManager.refresh_dependencies(False)
            DependencyManager.refresh_dependencies(True)
            return
        dependency_menu = {
            "selected_index": 2,
            "items": [
                ["Back", "Back to previous menu"],
                ["Add External .jar", "Add dependency .jar file"],
                ["Add Class Folder", "Add dependency class folder"]
            ],
            "actions": [
                {
                    "name": "project_settings"
                }
            ]
        }

        dependency_menu["actions"].extend([
            {
                "command": "javatar_settings",
                "args": {"actiontype": "add_external_jar", "arg1": from_global}
            },
            {
                "command": "javatar_settings",
                "args": {"actiontype": "add_class_folder", "arg1": from_global}
            }
        ])

        dependencies = DependencyManager.get_dependencies(from_global)
        for dependency in dependencies:
            name = basename(dependency[0])
            if dependency[1]:
                dependency_menu["actions"].append(
                    {
                        "command": "javatar_settings",
                        "args": {
                            "actiontype": "remove_dependency",
                            "arg1": dependency[0],
                            "arg2": False
                        }
                    }
                )
                if isdir(dependency[0]):
                    dependency_menu["items"].append([
                        "[" + name + "]",
                        "Global dependency. Select to remove from the list"
                    ])
                else:
                    dependency_menu["items"].append([
                        name,
                        "Global dependency. Select to remove from the list"
                    ])
            else:
                dependency_menu["actions"].append(
                    {
                        "command": "javatar_settings",
                        "args": {
                            "actiontype": "remove_dependency",
                            "arg1": dependency[0],
                            "arg2": True
                        }
                    }
                )
                if isdir(dependency[0]):
                    dependency_menu["items"].append([
                        "[" + name + "]",
                        "Project dependency. Select to remove from the list"
                    ])
                else:
                    dependency_menu["items"].append([
                        name,
                        "Project dependency. Select to remove from the list"
                    ])
        menu_name = "_dependencies"
        if from_global:
            menu_name = "global" + menu_name
        else:
            menu_name = "local" + menu_name
        sublime.active_window().run_command("javatar", {"replaceMenu": {
            "name": menu_name,
            "menu": dependency_menu
        }})
