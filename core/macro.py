import sublime
import os
from .regex import RE
from .state_property import StateProperty


class _Macro:
    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def get(self, macros=None, params=None):
        """
        Returns a list of available macros

        @param macros: a macros to be merged with
        @param params: parameters to pass to various macros
        """
        macros = macros or {}
        params = params or {}
        attrs = dir(self)
        macros["%"] = "%"
        reserved = ["macro"]
        # Create a macro name based on method name
        for attr in attrs:
            if attr.startswith("get_"):
                name = attr[4:].lower()
                if name in reserved:
                    continue
                args = []
                kwargs = {}
                if name in params:
                    if "args" in params[name]:
                        args = params[name]["args"]
                    if "kwargs" in params[name]:
                        kwargs = params[name]["kwargs"]
                macros[name] = getattr(self, attr)(*args, **kwargs)
        return macros

    def get_macro(self, match, macros=None):
        """
        Returns the result of macro for the RegEx match

        @param match: a RegEx match
        @param macros: a list of lookup macros
        """
        macros = macros or {}
        name = match.group(1).lower()
        sep = match.group(9) if match.group(8) else None
        output = macros[name] if name in macros else ""
        if match.group(2):
            if match.group(4):
                output = output[int(match.group(4))]
            elif match.group(5):
                if match.group(6) and match.group(7):
                    output = output[int(match.group(6)):int(match.group(7))]
                elif match.group(6):
                    output = output[int(match.group(6)):]
                elif match.group(7):
                    output = output[:int(match.group(7))]
        if sep:
            return sep.join(output)
        else:
            return str(output)

    def parse(self, string, macros=None):
        """
        Returns a macro-parsed string

        @param string: a string to parse
        @param macros: a list of lookup macros
        """
        macros = macros or self.get()
        return RE().get(
            "macro",
            "%(\\w+|\\%)(\\[((\\d*)|((\\d*):(\\d*)))\\])?(<(.?)>)?%"
        ).sub(
            lambda m: self.get_macro(m, macros),
            string
        )

    def get_sep(self, *args, **kwargs):
        return os.sep

    def get_file(self, *args, **kwargs):
        return StateProperty().get_file(*args, **kwargs)

    def get_project_dirs(self, *args, **kwargs):
        return StateProperty().get_project_dirs(*args, **kwargs)

    def get_source_folders(self, *args, **kwargs):
        return StateProperty().get_source_folders(*args, **kwargs)

    def get_source_folder(self, *args, **kwargs):
        return StateProperty().get_source_folder(*args, **kwargs)

    def get_root_dir(self, *args, **kwargs):
        return StateProperty().get_root_dir(*args, **kwargs)

    def get_current_dir(self, *args, **kwargs):
        return StateProperty().get_dir(*args, **kwargs)

    def get_project_dirs_prefix(self, *args, **kwargs):
        return os.path.commonprefix(StateProperty().get_project_dirs(
            *args, **kwargs
        ))

    def get_source_folders_prefix(self, *args, **kwargs):
        return os.path.commonprefix(StateProperty().get_source_folders(
            *args, **kwargs
        ))

    def get_packages_path(self, *args, **kwargs):
        return sublime.packages_path()


def Macro():
    return _Macro.instance()
