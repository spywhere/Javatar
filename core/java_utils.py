import sublime
import os
from .regex import RE
from .state_property import StateProperty


class JavaClass:

    """
    A class represents a Java class
    """

    def __init__(self, jclass):
        self.jclass = jclass or ""

    def is_empty(self):
        """
        Returns whether class is empty
        """
        return not self.jclass

    def get(self):
        """
        Returns a class
        """
        return self.jclass


class JavaPackage:

    """
    A class represents a Java package
    """

    def __init__(self, jpackage):
        self.package_paths = []
        if isinstance(jpackage, str):
            match = RE.search("package_class_match", jpackage)
            if match:
                self.package_paths = JavaUtils.normalize_package_path(
                    match.group(1)
                ).split(".")
        elif isinstance(jpackage, list):
            self.package_paths = jpackage
        elif isinstance(jpackage, tuple):
            self.package_paths = list(jpackage)

    def join(self, package):
        """
        Returns a joined package

        @param package: a package to join with
        """
        return JavaPackage(self.package_paths + package.package_paths)

    def is_empty(self):
        """
        Returns whether package is empty
        """
        return not self.package_paths

    def as_path(self):
        """
        Returns package as a file path
        """
        return os.path.join(*self.package_paths)

    def as_class_path(self):
        """
        Returns a package as a class path
        """
        return ".".join(self.package_paths)


class JavaClassPath:

    """
    A class represents a Java class path
    """

    def __init__(self, path):
        self.package = None
        self.jclass = None
        if isinstance(path, str):
            match = RE.search("package_class_match", path)
            if match:
                self.package = JavaPackage(
                    JavaUtils.normalize_package_path(match.group(1)).split(".")
                )
                self.jclass = JavaClass(
                    JavaUtils.normalize_package_path(match.group(4))
                )

    def get_package(self):
        """
        Returns a package within class path
        """
        return self.package

    def get_class(self):
        """
        Returns a class within class path
        """
        return self.jclass

    def as_path(self):
        """
        Returns class path as a file path
        """
        return os.path.join(self.package.as_path(), self.jclass.get())

    def as_class_path(self):
        """
        Returns a proper class path
        """
        return ".".join([self.package.as_class_path(), self.jclass.get()])


class JavaUtils:

    """
    Java-related utilities
    """

    @staticmethod
    def to_readable_class_path(class_path, as_package=False):
        """
        Returns a class path that can be read easily by human

        @param class_path: an original class path to be parsed
        @param as_package: a boolean indicated if the class path is already
            a package path or not
        """
        if not as_package:
            class_path = JavaUtils.to_package(class_path).as_class_path()
        if not class_path:
            if StateProperty.is_project():
                class_path = "(Default Package)"
            else:
                class_path = "(Unknown Package)"
        return class_path

    @staticmethod
    def is_class_path(class_path, special=False):
        """
        Returns whether specified class path is a valid class path

        @param class_path: a class path to be validated
        @param special: a boolean indicated if the class path is a special case
            (contains inheritance selectors) or not
        """
        return RE.match(
            "special_package_name_match" if special else "package_name_math",
            class_path
        ) is not None

    @staticmethod
    def normalize_package_path(class_path):
        """
        Returns a dot-trimmed class path

        @param class_path: a class path to be trimmed
        """
        return RE.get("normalize_package_path", "^\\.*|\\.*$").sub("", class_path)

    @staticmethod
    def to_package(path, relative=True):
        """
        Returns a Java package from specified path

        @param path: a path to be converted
        @param relative: a boolean indicated if the path should be converted to
            relative path or not
        """
        from ..utils import Utils
        if relative:
            path = os.path.relpath(path, StateProperty.get_root_dir())
        class_path = ".".join(Utils.split_path(path))
        return JavaPackage(
            JavaUtils.normalize_package_path(class_path).split(".")
        )

    @staticmethod
    def create_package_path(path, silent=False):
        """
        Creates a directory for specified path and returns the status

        @param path: a path to be created
        @param silent: a boolean indicated if the operation should be silent
            or not
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except BaseException as e:
                sublime.error_message(
                    "Error while create a package: {exception}".format_map({
                        "exception": e
                    })
                )
                return False
        else:
            if not silent:
                sublime.message_dialog("Package is already exists")
            return False
        return True
