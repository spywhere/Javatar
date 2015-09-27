import sublime
import os
import shlex
from .dependency_manager import DependencyManager
from .generic_shell import GenericBlockShell


class _HelperService:

    """
    A Javatar autocomplete helper class for deep Java information query
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
        self.actions = []

    def query_data(self, query):
        from .jdk_manager import JDKManager
        helper = sublime.find_resources("JavatarAutocompleteHelper.jar")
        if not helper:
            return None
        helper = helper[0]
        if helper[:9] == "Packages/":
            helper = os.path.join(sublime.packages_path(), helper[9:])
        executable = JDKManager().get_executable("run")
        if not executable:
            return None

        dependencies = [
            dependency[0]
            for dependency
            in DependencyManager().get_dependencies()
        ]
        runtime_path = JDKManager().get_runtime_file("runtime")
        if runtime_path:
            dependencies.append(runtime_path)
        cps = os.pathsep.join(dependencies)
        helper_script = "%s -jar %s -cp %s %s" % (
            shlex.quote(executable),
            shlex.quote(helper),
            shlex.quote(cps),
            query
        )
        return GenericBlockShell().run(helper_script)

    def get_packages(self):
        query = "-p"
        output = self.query_data(query)
        packages = []
        if output and output["data"] and output["return_code"] == 0:
            packages = output["data"].strip().split("\n")
        return packages

    def get_class_paths_for_class(self, class_name):
        query = "-t %s" % (class_name)
        output = self.query_data(query)
        class_paths = []
        if output and output["data"] and output["return_code"] == 0:
            class_paths = output["data"].strip().split("\n")
        return class_paths


def HelperService():
    return _HelperService.instance()
