import sublime
import os
import time
import math
from .action_history import ActionHistory
from .java_utils import JavaUtils
from .settings import Settings
from .state_property import StateProperty
from .status_manager import StatusManager
from .thread_progress import MultiThreadProgress


class _BuildSystem:
    """
    A multi-thread build system
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.log_view = None
        self.reset()

    def reset(self):
        """
        Reset the instance variables to clear the build
        """
        self.failed = False
        self.building = False
        self.builders = []
        self.create_log = False
        self.finish_callback = None
        self.cancel_callback = None

    def create_builder(self, files=None, macro_data=None):
        """
        Creates and run a builder thread for specified files

        @param files: a list of file paths
        """
        if not files:
            return
        from ..threads import BuilderThread
        macro_data = macro_data or {}
        builder = BuilderThread(self, files, macro_data, files)
        self.progress.add(builder, "")
        if not self.progress.running:
            self.progress.run()
        self.builders.append(builder)

    def on_builder_complete(self, total_files, elapse_time, data, ret, params):
        """
        A callback for the builder thread

        @param total_files: a total number of files passed to the builder
        @param elapse_time: a total time to build the files
        @param data: a returned data from the process
        @param ret: a return code from the process
        @param params: an additional parameters passed to the builder
        """
        if self.create_log and (
            not self.log_view or not self.log_view.id()
        ):
            self.cancel_build()
            return
        if ret != 0:
            self.failed = True
        else:
            self.update_cache_for_files(params)
        self.current_progress += total_files
        self.progress.set_message("Building %s of %s file%s... %.2f%%" % (
            self.current_progress,
            self.total_progress,
            "s" if self.total_progress > 1 else "",
            self.current_progress * 100 / self.total_progress
        ))

        if data:
            if not self.create_log and not self.log_view:
                target_group, target_index = Settings().get_view_index(
                    "build_log_target_group"
                )
                self.create_log = True
                self.log_view = self.window.new_file()
                self.window.set_view_index(
                    self.log_view,
                    target_group,
                    target_index
                )
                self.log_view.set_name("Preparing build log...")
                self.log_view.set_syntax_file(
                    "Packages/Javatar/syntax/JavaCompilationError.tmLanguage"
                )
                # Prevent view access while creating which cause
                #    double view to create
                time.sleep(Settings().get("build_log_delay"))
            self.log_view.set_scratch(True)
            self.log_view.run_command("javatar_utils", {
                "util_type": "add",
                "text": data
            })

    def on_build_complete(self):
        """
        A callback when the build process is finish
        """
        if self.create_log and (
            not self.log_view or not self.log_view.id()
        ):
            StatusManager().show_notification("Building Cancelled")
            StatusManager().show_status("Building Cancelled", target="build")
            ActionHistory().add_action(
                "javatar.core.build_system.on_build_complete",
                "Building Cancelled"
            )
            if self.cancel_callback:
                self.cancel_callback()
            return

        if self.failed:
            message = "Building Failed [{0:.2f}s]"
        elif self.create_log:
            message = "Building Finished with Warning [{0:.2f}s]"
        else:
            message = "Building Finished [{0:.2f}s]"

        time_diff = time.time() - self.start_time
        StatusManager().show_notification(message.format(time_diff))
        self.build_size = -1
        if self.log_view:
            self.log_view.set_name(message.format(time_diff))
        StatusManager().show_status(message.format(time_diff), target="build")
        ActionHistory().add_action(
            "javatar.core.build_system.on_build_complete",
            message.format(time_diff)
        )
        if self.finish_callback:
            self.finish_callback(self.failed)
        self.reset()

    def cancel_build(self):
        """
        Cancels all running builders
        """
        if not self.building:
            return
        for builder in self.builders:
            builder.cancel()
        self.building = False

    def trim_extension(self, file_path):
        """
        Remove a file extension from the file path

        @param file_path: a file path to remove an extension
        """
        filename, ext = os.path.splitext(os.path.basename(file_path))
        for extension in Settings().get("java_extensions"):
            if ext == extension:
                return file_path[:-len(ext)]
        return file_path

    def update_cache_for_files(self, files):
        if Settings().get("always_rebuild"):
            return
        cache = StateProperty().load_cache()
        if "build_cache" not in cache:
            cache["build_cache"] = {}
        for file_path in files:
            modified_time = int(os.path.getmtime(file_path))
            full_class_path = JavaUtils().to_package(
                self.trim_extension(file_path)
            ).as_class_path()
            cache["build_cache"][full_class_path] = modified_time
        StateProperty().save_cache(cache)

    def is_file_changed(self, file_path):
        """
        Returns whether the specified file path has been modified or not

        @param file_path: a file path to check (must exists)
        """
        if Settings().get("always_rebuild"):
            return True
        modified_time = int(os.path.getmtime(file_path))
        cache = StateProperty().load_cache()
        if "build_cache" not in cache:
            cache["build_cache"] = {}
        full_class_path = JavaUtils().to_package(
            self.trim_extension(file_path)
        ).as_class_path()
        if full_class_path not in cache["build_cache"]:
            return True
        return cache["build_cache"][full_class_path] != modified_time

    def build_files(self, files=None, window=None):
        """
        Calculate and assigns file paths to builder threads

        @param files: a list of file paths
        """
        self.log_view = None
        self.window = window or sublime.active_window()
        if self.building:
            self.cancel_build()
        if not files:
            return "No class to build"
        self.start_time = time.time()
        if not Settings().get("always_rebuild"):
            files = [
                file_path
                for file_path in files
                if self.is_file_changed(file_path)
            ]
            if not files:
                self.on_build_complete()

        from .jdk_manager import JDKManager
        macro_data = {}
        executable_name = JDKManager().get_executable("build")
        if not executable_name:
            return "Build executable is not found"

        self.building = True
        self.progress = MultiThreadProgress(
            "Preparing build",
            on_all_complete=self.on_build_complete,
            target="build"
        )
        self.current_progress = 0
        self.total_progress = len(files)
        per_thread = math.ceil(
            len(files) / Settings().get("builder_threads", 1)
        )
        self.progress.set_message("Building %s of %s file%s... %.2f%%" % (
            self.current_progress,
            self.total_progress,
            "s" if self.total_progress > 1 else "",
            self.current_progress * 100 / self.total_progress
            if self.total_progress > 0 else 0
        ))
        while files:
            self.create_builder(files[:per_thread], macro_data=macro_data)
            files = files[per_thread:]
        return None

    def build_dir(self, dir_path=None, window=None):
        """
        Builds all files within a specified directory

        @param dir_path: a directory path
        """
        if not dir_path:
            return False
        return self.build_files(self.get_files(dir_path), window=window)

    def build_dirs(self, dir_paths=None, window=None):
        """
        Builds all files within specified directories

        @param dir_paths: a list of directory path
        """
        if not dir_paths:
            return False
        files = []
        for dir_path in dir_paths:
            files += self.get_files(dir_path)
        if not files:
            return False
        return self.build_files(files, window=window)

    def get_files(self, dir_path=None):
        """
        Returns a list of file paths in specified directory and its
            sub-directory

        @param dir_path: a directory path
        """
        if not dir_path:
            return []
        files = []
        for name in os.listdir(dir_path):
            path_name = os.path.join(dir_path, name)
            if (os.path.isdir(path_name) and
                    name not in Settings().get_sublime(
                        "folder_exclude_patterns", []
                    )):
                files += self.get_files(path_name)
            elif (os.path.isfile(path_name) and
                    JavaUtils().is_java_file(path_name)):
                files.append(path_name)
        return files


def BuildSystem():
    return _BuildSystem.instance()
