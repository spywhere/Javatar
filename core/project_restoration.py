import sublime
from .logger import Logger
from .settings import Settings


class _ProjectRestoration:

    """
    Save/Load project state to keep track of settings without saving project
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.loaded = False

    def save_state(self, repeat=False):
        """
        Save project state into global settings file

        @param repeat: if provided as True, will re-save the project state
            again after specified time period
        """
        if not self.loaded:
            return
        if Settings().get("allow_project_restoration"):
            project_data = {
                str(window.id()): window.project_data()
                for window in sublime.windows()
            }
            Settings().set("project_data", project_data, to_global=True)
            if repeat:
                sublime.set_timeout(
                    self.save_state,
                    Settings().get("project_update_interval")
                )

    def load_state(self):
        """
        Load project state from global settings file into windows

        This method should also start the save state interval
        """
        if Settings().get("allow_project_restoration"):
            project_data = Settings().get_global("project_data")
            if project_data:
                for window in sublime.windows():
                    if str(window.id()) in project_data:
                        window.set_project_data(project_data[str(window.id())])
                        Logger().debug(
                            "Restore project data on window %s" %
                            (str(window.id()))
                        )
            self.loaded = True
            self.save_state(repeat=True)


def ProjectRestoration():
    return _ProjectRestoration.instance()
