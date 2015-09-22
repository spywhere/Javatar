import sublime
import os
from .regex import RE
from .state_property import StateProperty
from .settings import Settings


class JavaClass:

    """
    A class represents a Java class
    """

    def __init__(self, jclass=None):
        self.jclass = jclass or ""

    def is_empty(self):
        """
        Returns whether a class is empty
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

    def __init__(self, jpackage=None):
        self.package_paths = []
        if isinstance(jpackage, str) and jpackage:
            match = RE().search("package_path_match", jpackage)
            if match:
                self.package_paths = JavaUtils().normalize_package_path(
                    match.group(0)
                ).split(".")
        elif isinstance(jpackage, list) or isinstance(jpackage, tuple):
            self.package_paths = [com for com in jpackage if com]

    def join(self, package):
        """
        Returns a joined package

        @param package: a package to join with
        """
        return JavaPackage(self.package_paths + package.package_paths)

    def is_empty(self):
        """
        Returns whether a package is empty
        """
        return not self.package_paths

    def as_list(self):
        """
        Returns package as a component list
        """
        return self.package_paths

    def as_path(self):
        """
        Returns package as a file path
        """
        if self.is_empty():
            return ""
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

    def __init__(self, class_path=None):
        self.package = JavaPackage()
        self.jclass = JavaClass()
        if isinstance(class_path, str) and class_path:
            match = RE().match("class_path_match", class_path)
            if match:
                self.package = JavaPackage(
                    JavaUtils().normalize_package_path(
                        match.group(1)
                    ).split(".")
                )
                self.jclass = JavaClass(
                    JavaUtils().normalize_package_path(match.group(3))
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
        if self.package.is_empty():
            return self.jclass.get()
        elif self.jclass.is_empty():
            return self.package.as_class_path()
        return ".".join([
            x for x in
            [self.package.as_class_path(), self.jclass.get()]
            if x
        ])


class _JavaUtils:

    """
    Java-related utilities
    """

    CREATE_SUCCESS = 0
    CREATE_EXISTS = 1
    CREATE_ERROR = 2

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def to_readable_class_path(self, path, as_class_path=False):
        """
        Returns a class path that can be read easily by human

        @param path: an original path to be parsed
        @param as_class_path: a boolean indicated if the path is already
            a class path or not
        """
        if not as_class_path:
            path = self.to_package(path).as_class_path()
        if not path:
            if StateProperty().is_project():
                return "(Default Package)"
            else:
                return "(Unknown Package)"
        return path

    def is_java(self, view=None):
        """
        Returns whether specified view is a Java file or not

        @param view: a view to be validated
        """
        view = view or sublime.active_window().active_view()
        if not view:
            return False
        if view.file_name():
            return self.is_java_file(view.file_name())
        return view.find_by_selector(Settings().get("java_source_selector"))

    def is_java_file(self, file_path):
        """
        Returns whether specified file path is a Java file

        @param file_path: a file path to be validated
        """
        if file_path is None:
            return False
        _, ext = os.path.splitext(os.path.basename(file_path))
        return ext in Settings().get("java_extensions")

    def is_class_path(self, class_path, special=False):
        """
        Returns whether specified class path is a valid class path

        @param class_path: a class path to be validated
        @param special: a boolean indicated if the class path is a special case
            (contains inheritance selectors) or not
        """
        match = RE().match(
            "special_class_path_match" if special else "class_path_match",
            class_path
        )
        return match is not None

    def normalize_package_path(self, class_path):
        """
        Returns a dot-trimmed class path

        @param class_path: a class path to be trimmed
        """
        return RE().get("normalize_package_path", "^\\.*|\\.*$").sub(
            "", class_path
        )

    def to_package(self, path, relative=True):
        """
        Returns a Java package from specified path

        @param path: a path to be converted
        @param relative: a boolean indicated if the path should be converted to
            relative path or not
        """
        from ..utils import Utils
        if relative:
            convert = False
            for source_folder in StateProperty().get_source_folders():
                if Utils().contains_file(source_folder, path):
                    convert = True
                    path = os.path.relpath(path, source_folder)
                    break
            if not convert:
                path = os.path.relpath(
                    path, StateProperty().get_source_folder()
                )
        class_path = ".".join(Utils.split_path(path))
        return JavaPackage(
            self.normalize_package_path(class_path).split(".")
        )

    def create_package_path(self, path, silent=False):
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
                    "Error while create a package" +
                    " \"{package}\": {exception}".format_map({
                        "package": path,
                        "exception": e
                    })
                )
                return self.CREATE_ERROR
        else:
            if not silent:
                sublime.message_dialog("Package is already exists")
            return self.CREATE_EXISTS
        return self.CREATE_SUCCESS


def JavaUtils():
    return _JavaUtils.instance()
