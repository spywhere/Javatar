import sublime


class _Settings:

    """
    Settings collections for easier access and managements
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.reset()

    def reset(self):
        """
        Reset all changes (used on restart)
        """
        self.settings = None
        self.sublime_settings = None
        self.settings_base = "Javatar.sublime-settings"
        self.sublime_base = "Preferences.sublime-settings"

    def startup(self):
        """
        Read all settings from files
        """
        self.settings = sublime.load_settings(self.settings_base)
        self.sublime_settings = sublime.load_settings(self.sublime_base)

    def get_global(self, key, default=None, as_tuple=False):
        """
        Returns a value in default settings file

        @param key: a key to get value
        @param default: a return value if specified key is not exists
        @param as_tuple: a boolean specified whether returns as a tuple contains
            value and a boolean specified if value gather from project
            settings or not
        """
        if as_tuple:
            return (self.get_global(key, default, as_tuple=False), False)
        else:
            return self.settings.get(key, default)

    def get_local(self, key, default=None, as_tuple=False):
        """
        Returns a value in project settings file

        @param key: a key to get value
        @param default: a return value if specified key is not exists
        @param as_tuple: a boolean specified whether returns as a tuple contains
            value and a boolean specified if value gather from project
            settings or not
        """
        if as_tuple:
            return (self.get_local(key, default, as_tuple=False), True)
        else:
            project_data = sublime.active_window().project_data()
            if (project_data is not None and
                    "javatar" in project_data and
                    key in project_data["javatar"]):
                return project_data["javatar"][key]
        return default

    def get_sublime(self, key, default=None):
        """
        Returns a value in Sublime Text's settings file

        @param key: a key to get value
        @param default: a return value if specified key is not exists
        """
        return self.sublime_settings.get(key, default)

    def get(self, key, default=None, from_global=None, as_tuple=False):
        """
        Returns a value in settings

        @param key: a key to get value
        @param default: a return value if specified key is not exists
        @param as_tuple: a boolean specified whether returns as a tuple contains
            value and a boolean specified if value gather from project
            settings or not

        This method must return in local-default prioritize order
        """
        if from_global is None:
            value = self.get(
                key,
                default=None,
                from_global=False,
                as_tuple=as_tuple
            )
            if value is None:
                value = self.get(
                    key,
                    default=default,
                    from_global=True,
                    as_tuple=as_tuple
                )
            return value
        elif from_global:
            return self.get_global(key, default, as_tuple)
        else:
            return self.get_local(key, default, as_tuple)

    def set(self, key, val, to_global=False):
        """
        Set a value to specified key in settings

        @param key: a key to set value
        @param val: a value to be set, if provided as not None
            otherwise key will be deleted instead
        @param to_global: a boolean specified whether set the value to
            default settings or not
        """
        if to_global:
            if val is None:
                if self.settings.has(key):
                    self.settings.erase(key)
                else:
                    # Return here so it won't wasting time saving old settings
                    return
            else:
                self.settings.set(key, val)
            sublime.save_settings(self.settings_base)
        else:
            window = sublime.active_window()
            project_data = window.project_data()
            if val is None:
                if (project_data is not None and
                        "javatar" in project_data and
                        key in project_data["javatar"]):
                    del project_data["javatar"][key]
                else:
                    # Return here so it won't wasting time saving old settings
                    return
            else:
                if "javatar" in project_data:
                    data = project_data["javatar"]
                else:
                    data = {}
                data[key] = val
                project_data["javatar"] = data
            window.set_project_data(project_data)

    def ready(self):
        """
        Returns whether settings are ready to be used
        """
        return self.settings is not None


def Settings():
    return _Settings.instance()
