import sublime
from .logger import Logger
from .settings import Settings


class ProjectRestoration:

    """
    Save/Load project state to keep track of settings without saving project
    """

    loaded = False

    @staticmethod
    def save_state(repeat=False):
        """
        Save project state into global settings file

        @param repeat: if provided as True, will re-save the project state
            again after specified time period
        """
        if not ProjectRestoration.loaded:
            return
        if Settings.get("allow_project_restoration"):
            project_data = {
                str(window.id()): window.project_data()
                for window in sublime.windows()
            }
            Settings.set("project_data", project_data, to_global=True)
            if repeat:
                sublime.set_timeout(
                    ProjectRestoration.save_state,
                    Settings.get("project_update_interval")
                )

    @staticmethod
    def load_state():
        """
        Load project state from global settings file into windows

        This method should also start the save state interval
        """
        if Settings.get("allow_project_restoration"):
            project_data = Settings.get_global("project_data")
            if project_data:
                for window in sublime.windows():
                    if str(window.id()) in project_data:
                        window.set_project_data(project_data[str(window.id())])
                        Logger.debug(
                            "Restore project data on window %s" %
                            (str(window.id()))
                        )
            ProjectRestoration.loaded = True
            ProjectRestoration.save_state(repeat=True)
