import sublime
import hashlib
import os
import shlex
from .dependency_manager import DependencyManager
from .generic_shell import GenericBlockShell
from .logger import Logger
from .settings import Settings


class _HelperService:

    """
    A Javatar autocomplete helper class for deep Java information query
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def startup(self):
        """
        Check and extract helper files

        @param on_done: callback after loaded
        """
        helpers = sublime.find_resources("JavatarAutocompleteHelper.jar")
        installed = False
        for helper in helpers:
            if helper[:9] == "Packages/":
                helper = os.path.join(sublime.packages_path(), helper[9:])
            if os.path.exists(helper) and self.verify_helper(helper):
                installed = True
                break
        if not installed:
            Logger().info("Updating helper files...")
            file_path = os.path.join(
                sublime.packages_path(),
                "User",
                "Javatar",
                "Helper",
                "JavatarAutocompleteHelper.jar"
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            if not os.path.isdir(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except:
                    pass
            helper_file = open(file_path, "wb")
            helper_file.write(sublime.load_binary_resource(
                "Packages/Javatar/binary/JavatarAutocompleteHelper.jar"
            ))
            helper_file.close()

    def verify_helper(self, path):
        """
        Returns whether a specified helper file is valid helper file

        @param path: a path to helper file
        """

        helper_file = open(path, "rb")
        actual_hash = hashlib.sha256(
            helper_file.read()
        ).hexdigest()
        helper_file.close()
        expected_hash = hashlib.sha256(sublime.load_binary_resource(
            "Packages/Javatar/binary/JavatarAutocompleteHelper.jar"
        )).hexdigest()
        return actual_hash == expected_hash

    def query_data(self, query):
        from .jdk_manager import JDKManager
        helpers = sublime.find_resources("JavatarAutocompleteHelper.jar")
        helper_file = None
        for helper in helpers:
            if helper[:9] == "Packages/":
                helper = os.path.join(sublime.packages_path(), helper[9:])
            if os.path.exists(helper) and self.verify_helper(helper):
                helper_file = helper
                break
        if not helper_file:
            return None
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
        exclusion = Settings().get("java_exclude_packages", [])

        if exclusion:
            exclusion = " -xp %s" % (shlex.quote(os.pathsep.join(exclusion)))
        else:
            exclusion = ""
        if dependencies:
            dependencies = " -cp %s" % (shlex.quote(os.pathsep.join(dependencies)))
        else:
            dependencies = ""

        helper_script = "%s -jar %s%s%s %s" % (
            shlex.quote(executable),
            shlex.quote(helper_file),
            exclusion,
            dependencies,
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

    def get_class_paths_for_classes(self, class_names):
        query = "-t %s" % (os.pathsep.join(class_names))
        output = self.query_data(query)
        class_paths = {}
        if output and output["data"] and output["return_code"] == 0:
            paths = output["data"].strip().split("\n")
            for path in paths:
                name, class_path = path.split(";")
                if name in class_paths:
                    class_paths[name].append(class_path)
                else:
                    class_paths[name] = [class_path]
        return class_paths


def HelperService():
    return _HelperService.instance()
