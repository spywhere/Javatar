import sublime
import os
import threading
import shlex
from ..core import (
    ActionHistory,
    GenericBlockShell,
    JavatarDict,
    Logger,
    RE,
    Settings
)


class JDKDetectorThread(threading.Thread):

    """
    A thread to detect and update JDK versions
    """

    def __init__(self, silent=False, on_done=None):
        self.silent = silent
        self.on_done = on_done
        threading.Thread.__init__(self)

    @classmethod
    def get_jdk_version(cls, path=None, executable=None):
        """
        Test a specified JDK and returns its version

        @param path: a JDK installaltion path
        @param executable: an executable name to check, if provided,
            otherwise, will check all executables
        """
        path = path or ""
        if not executable:
            output_version = None
            exes = Settings().get("java_executables")
            if "version" in exes:
                version = JDKDetectorThread.get_jdk_version(
                    path, exes["version"]
                )
                if not version:
                    return None
                elif not output_version:
                    output_version = version
            return output_version
        executable = os.path.join(path, executable)
        output = GenericBlockShell().run(shlex.quote(executable) + " -version")
        if output["data"]:
            match = RE().search("java_version_match", output["data"])
            if match:
                version = {}
                if match.lastindex > 0:
                    version["version"] = match.group(1)
                    if match.lastindex > 1:
                        version["update"] = match.group(2)
                return version
        return None

    def is_java_home_path(self, path):
        """
        Check whether the specified path is contains all Java runtime files

        @param path: a directory path
        """
        required_files = set([
            file
            for files in
            Settings().get("java_runtime_files").values()
            for file in files
        ])

        existing_files = (
            name
            for name in os.listdir(path)
            if os.path.isfile(os.path.join(path, name))
        )
        return required_files.issubset(existing_files)

    def find_java_home(self, path):
        """
        Find all subfolder of specified path and return the path if it contains
            all Java runtime files

        @param path: a path to find
        """
        for name in os.listdir(path):
            path_name = os.path.join(path, name)
            if os.path.isdir(path_name):
                if self.is_java_home_path(path_name):
                    return os.path.dirname(path_name)
                java_home = self.find_java_home(path_name)
                if java_home:
                    return java_home
        return None

    def get_java_home(self, path=None):
        """
        Returns the Java home directory

        @param path: a path to Java executable files
        """
        path = path or ""
        exes = Settings().get("java_executables")
        if "script" not in exes:
            return None
        executable = os.path.join(path, exes["script"])
        gather_script = (
            "java.lang.System.out.println(" +
            "java.lang.System.getProperty(\"java.home\"));"
        )
        output = GenericBlockShell().run((
            shlex.quote(executable) +
            " -e " +
            shlex.quote(gather_script)
        ))
        if output["data"] and os.path.exists(output["data"]):
            return output["data"]
        if path:
            # Move one level up, so we ends up on the JDK root directory
            return self.find_java_home(os.path.dirname(path))
        return None

    def is_jdk_path(self, path):
        """
        Check whether the specified path is a JDK installation path

        @param path: a directory path
        """
        required_files = set(Settings().get("java_executables").values())

        existing_files = (
            os.path.splitext(name)
            for name in os.listdir(path)
            if os.path.isfile(os.path.join(path, name))
        )
        existing_files = (
            name
            for name, ext in existing_files
            if ext in {"", ".exe"}
        )
        return required_files.issubset(existing_files)

    @classmethod
    def to_readable_version(cls, jdk=None):
        """
        Convert a JDK dict to readable JDK string

        @param jdk: a JDK dict
        """
        if not jdk:
            return ""
        v = "JDK" + jdk["version"]
        if "update" in jdk:
            v += "u" + jdk["update"]
        return v

    def find_jdk_dirs(self, path):
        """
        Find all subfolder of specified path and returns all JDK installation
            directories

        @param path: a path to find
        """
        jdk_dirs = {}
        for name in os.listdir(path):
            path_name = os.path.join(path, name)
            if os.path.isdir(path_name):
                if self.is_jdk_path(path_name):
                    version = self.get_jdk_version(path_name)
                    java_home = self.get_java_home(path_name)
                    if version and java_home:
                        jdk = {
                            "bin": path_name,
                            "home": java_home,
                            "version": version["version"]
                        }
                        if "update" in version:
                            jdk["update"] = version["update"]
                        jdk_dirs[self.to_readable_version(version)] = jdk
                dirs = self.find_jdk_dirs(path_name)
                for key in dirs:
                    jdk_dirs[key] = dirs[key]
        return jdk_dirs

    def get_latest_jdk(self, jdks):
        """
        Returns a latest JDK in the dict

        @param jdks: a JDKs dict
        """
        jdk_version = [
            jdk
            for jdk in jdks
            if jdk != "use"
        ]
        if jdk_version:
            jdk_version.sort(reverse=True)
            return jdk_version[0]
        return None

    def verify_jdks(self, jdks=None):
        """
        Verify the JDK settings and update it

        @param jdks: a JDKs in JavatarDict format to be verified
        """
        jdks = jdks or JavatarDict(
            Settings().get_global("jdk_version"),
            Settings().get_local("jdk_version")
        )

        if jdks.has("use"):
            if jdks.get("use") == "" and jdks.has("home") and jdks.get("home"):
                version = self.get_jdk_version()
                if version:
                    Logger().info(
                        "Use default settings [%s]" % (
                            self.to_readable_version(version)
                        )
                    )
                    return jdks
            if jdks.has(jdks.get("use")):
                jdk = jdks.get(jdks.get("use"))
                if ("path" in jdk and
                    "version" in jdk and
                    os.path.exists(jdk["path"]) and
                        self.is_jdk_path(jdk["path"])):
                    Logger().info(
                        "Use selected JDK [%s]" % (
                            self.to_readable_version(jdk)
                        )
                    )
                    return jdks
            jdks.set(jdks.get("use"), None)
            jdks.set("use", None)
            jdks.set("home", None)
            return self.verify_jdks(jdks)
        platform = sublime.platform()
        installaltion_paths = Settings().get("jdk_installation")
        default = self.get_jdk_version()
        java_home = self.get_java_home()
        if default and java_home:
            Logger().info(
                "Use default JDK [%s]" % (
                    self.to_readable_version(default)
                )
            )
            jdks.set("use", "")
            jdks.set("home", java_home)

        if platform in installaltion_paths:
            jdk_paths = installaltion_paths[platform]
            java_home_env = os.getenv("JAVA_HOME")
            if java_home_env:
                java_home_env = os.path.dirname(java_home_env)
                if java_home_env not in jdk_paths:
                    jdk_paths.append(java_home_env)
            for path in jdk_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    dirs = self.find_jdk_dirs(path)
                    for key in dirs:
                        jdks.set(key, dirs[key])
        if not jdks.has("use") and jdks.get_dict():
            latest_jdk = self.get_latest_jdk(jdks.get_dict())
            if not latest_jdk:
                return None
            Logger().info(
                "Use latest JDK [%s]" % (
                    latest_jdk
                )
            )
            jdks.set("use", latest_jdk)
            jdks.set("home", None)
        return jdks

    def run(self, renew=False):
        """
        Detect and update the JDK versions for projects
        """
        try:
            jdks = self.verify_jdks()
            if jdks and jdks.get_dict():
                if jdks.is_global_change():
                    Settings().set("jdk_version", jdks.get_global_dict(), True)
                if jdks.is_local_change():
                    Settings().set("jdk_version", jdks.get_local_dict())
            else:
                Settings().set("jdk_version", None)
                Settings().set("jdk_version", None, True)
                Logger().info("No JDK found")
                sublime.error_message(
                    "Javatar cannot find JDK installed on your computer." +
                    "\n\nPlease install or settings the location of installed" +
                    " JDK."
                )
            if self.on_done:
                self.on_done(jdks)
            self.result = True
        except Exception as e:
            ActionHistory().add_action(
                "javatar.threads.jdk_manager.jdk_detector",
                "JDK Detection Error",
                e
            )
            self.result = False
