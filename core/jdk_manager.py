import os.path
from .action_history import ActionHistory
from .dict import JavatarDict
from .thread_progress import ThreadProgress
from .settings import Settings
from ..threads import JDKDetectorThread


class _JDKManager:

    """
    Detect and store JDK installation informations
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.reset(silent=True)

    def reset(self, silent=False):
        """
        Resets all stored data
        """
        if not silent:
            ActionHistory().add_action(
                "javatar.core.jdk_manager.reset", "Reset all JDKs"
            )
        self.jdks = None

    def on_jdk_detected(self, jdks, on_done=None):
        """
        Callback after JDKs are detected

        @param jdks: JDKs informations
        """
        self.jdks = jdks
        if on_done:
            on_done()

    def detect_jdk(self, silent=False, on_done=None, progress=False):
        """
        Detects installed JDKs

        @param silent: a boolean specified whether to print selected JDK to
            console or not
        @param on_done: a callback when JDKs has been detected
        @param progress: a boolean specified whether to show a progress in the
            status or not
        """
        thread = JDKDetectorThread(
            silent,
            lambda jdks: self.on_jdk_detected(jdks, on_done)
        )
        if progress:
            ThreadProgress(
                thread, "Detecting installed JDKs",
                "JDKs has been successfully detected"
            )
        else:
            thread.start()

    def get_default_jdk(self, jdks=None):
        """
        Returns the default JDK that Javatar is using from the specified JDKs

        @param jdks: a JDKs to check against
        """
        jdks = jdks or JavatarDict(
            Settings().get_global("jdk_version"),
            Settings().get_local("jdk_version")
        )
        if not jdks.has("use"):
            return None
        if jdks.get("use") == "" and jdks.get("home"):
            return {"bin": "", "home": jdks.get("home")}
        elif jdks.has(jdks.get("use")):
            return jdks.get(jdks.get("use"))
        return None

    def get_jdk_version(self, path=None, executable=None):
        """
        Test a specified JDK and returns its version

        @param path: a JDK installaltion path
        @param executable: an executable name to check, if provided,
            otherwise, will check all executables
        """
        return JDKDetectorThread.get_jdk_version(path, executable)

    def to_readable_version(self, jdk=None):
        """
        Convert a JDK dict to readable JDK string

        @param jdk: a JDK dict
        """
        return JDKDetectorThread.to_readable_version(jdk)

    def get_executable(self, key, path=None):
        """
        Returns a path to specified executable file

        @param key: a key for the Java executable
        @param path: a path to use for the executable
        """
        if key not in Settings().get("java_executables", {}):
            return None
        if path is None:
            jdk = self.get_default_jdk()
            if not jdk:
                return None
            path = jdk["bin"]
        return os.path.join(path, Settings().get("java_executables")[key])

    def get_runtime_file(self, key, path=None):
        """
        Returns a path to specified runtime file

        @param key: a key for the Java runtime files
        @param path: a path to use for the runtime file
        """
        if key not in Settings().get("java_runtime_files", {}):
            return None
        if path is None:
            jdk = self.get_default_jdk()
            if not jdk:
                return None
            path = jdk["home"]
        if path is None:
            return None
        names = Settings().get("java_runtime_files")[key]
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path) and file_name in names:
                return file_path
            elif os.path.isdir(file_path):
                file_path = self.get_runtime_file(key, file_path)
                if file_path:
                    return file_path
        return None

    def startup(self, on_done=None):
        """
        Detect installed JDK

        @param on_done: callback after detected
        """
        self.detect_jdk(
            on_done=on_done
        )

    def ready(self):
        """
        Returns whether manager ready to be used
        """
        return self.jdks is not None


def JDKManager():
    return _JDKManager.instance()
