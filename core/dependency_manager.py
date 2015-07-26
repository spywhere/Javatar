import sublime
import os.path
from .settings import Settings


class _DependencyManager:

    """
    Load and store all dependencies
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def startup(self):
        """
        Refresh dependencies list after start up
        """
        self.refresh_dependencies()

    def get_dependencies(self, from_global=False):
        """
        Returns dependency list

        @param from_global: a boolean specified whether returns a dependency
            list from global settings or local settings
        """
        out_dependencies = []
        dependencies = Settings().get("dependencies", from_global=from_global)

        if dependencies is not None:
            out_dependencies.extend(
                [dependency, from_global]
                for dependency in dependencies
                if os.path.exists(dependency)
            )

        if not from_global:
            out_dependencies.extend(
                [dependency, True]
                for dependency in Settings().get("dependencies", from_global=True)
                if os.path.exists(dependency)
            )

        return out_dependencies

    def refresh_dependencies(self, from_global=None):
        """
        Refresh dependency list

        @param from_global: a settings scope
            if provided as None, will refresh all dependencies
            if provided as True, will refresh only global dependencies settings
            if provided as False, will refresh only local dependencies settings
        """
        if from_global is None:
            self.refresh_dependencies(False)
            self.refresh_dependencies(True)
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
                "command": "javatar_project_settings",
                "args": {
                    "action_type": "add_external_jar",
                    "to_global": from_global
                }
            },
            {
                "command": "javatar_project_settings",
                "args": {
                    "action_type": "add_class_folder",
                    "to_global": from_global
                }
            }
        ])

        dependencies = self.get_dependencies(from_global)
        for dependency in dependencies:
            name = os.path.basename(dependency[0])
            if dependency[1]:
                dependency_menu["actions"].append(
                    {
                        "command": "javatar_project_settings",
                        "args": {
                            "action_type": "remove_dependency",
                            "dependency": dependency[0],
                            "from_global": True
                        }
                    }
                )
                if os.path.isdir(dependency[0]):
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
                        "command": "javatar_project_settings",
                        "args": {
                            "action_type": "remove_dependency",
                            "dependency": dependency[0],
                            "from_global": False
                        }
                    }
                )
                if os.path.isdir(dependency[0]):
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


def DependencyManager():
    return _DependencyManager.instance()
