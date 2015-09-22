import threading
import shlex
from os.path import isdir, isfile
from os import makedirs, pathsep
from ..core import (
    DependencyManager,
    GenericSilentShell,
    Settings,
    StateProperty
)


class BuilderThread(threading.Thread):

    """
    A thread to build Java source code files
    """

    def __init__(self, controller, files=None, macro_data=None, params=None):
        self.files = files or []
        self.total_files = len(self.files)
        self.macro_data = macro_data or {}
        self.params = params
        self.controller = controller
        self.running = True
        self.builds = 0
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        """
        Build the specified files
        """
        from ..core import JDKManager, Macro
        sourcepath = pathsep.join(StateProperty().get_source_folders())
        dependencies = ["."] + [
            dependency[0]
            for dependency
            in DependencyManager().get_dependencies()
        ]
        classpath = pathsep.join(dependencies)
        output_location = Macro().parse(Settings().get("build_output_location"))

        executable = JDKManager().get_executable("build")
        if not executable:
            return

        build_script = "%s -sourcepath %s -classpath %s" % (
            shlex.quote(executable),
            shlex.quote(sourcepath),
            shlex.quote(classpath)
        )
        if output_location:
            if isfile(output_location):
                return
            elif not isdir(output_location):
                try:
                    makedirs(output_location)
                except:
                    pass
            build_script += " -d %s" % (shlex.quote(output_location))

        while self.running and self.files:
            self.builds += 1
            parallel_builds = Settings().get("parallel_builds")
            if parallel_builds > 0:
                files = self.files[:parallel_builds]
                self.files = self.files[parallel_builds:]
            else:
                files = self.files
                self.files = []
            file_list = " ".join([
                shlex.quote(filename) for filename in files
            ])
            actual_build_script = build_script + " %s" % (file_list)
            build_args = Settings().get("build_arguments", "")
            if build_args:
                actual_build_script += " " + build_args

            shell = GenericSilentShell(
                actual_build_script,
                lambda elapse_time, data, ret, params: self.on_build_done(
                    len(files), elapse_time, data, ret
                )
            )
            shell.set_cwd(Macro().parse(Settings().get("build_location")))
            shell.start()
        while self.running and self.builds > 0:
            pass

    def on_build_done(self, total_files, elapse_time, data, ret):
        """
        Report the build result to the main builder controller
        """
        self.builds -= 1
        self.controller.on_builder_complete(
            total_files, elapse_time, data, ret, self.params
        )

    def cancel(self):
        """
        Cancel the build process
        """
        self.running = False
