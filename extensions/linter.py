import sublime
from os import pathsep, makedirs
from os.path import isfile, isdir
from ..core import (
    DependencyManager,
    JDKManager,
    Macro,
    StateProperty,
    Settings
)
from SublimeLinter.lint import Linter, util


class JavatarLinter(Linter):
    """
    Javatar's implementation of javac linter for SublimeLinter
    """

    executable = JDKManager().get_executable("lint") or "javac"
    syntax = "java"
    version_args = "-version"
    version_re = r"(?P<version>\d+\.\d+\.\d+)"
    version_requirement = ">= 1.7"
    regex = (
        r"^(?P<file>.+?):(?P<line>\d+): "
        r"(?:(?P<error>error)|(?P<warning>warning)): "
        r"(?:\[.+?\] )?(?P<message>[^\r\n]+)\r?\n"
        r"[^\r\n]+\r?\n"
        r"(?P<col>[^\^]*)\^"
    )
    multiline = True
    tempfile_suffix = "-"
    error_stream = util.STREAM_STDERR
    comment_re = r"\s*/[/*]"

    def cmd(self):
        """
        Returns the command to be used by SublimeLinter
        """

        sourcepath = pathsep.join(StateProperty().get_source_folders())
        dependencies = StateProperty().get_source_folders() + [
            dependency[0]
            for dependency
            in DependencyManager().get_dependencies()
        ]
        output_location = Macro().parse(Settings().get("build_output_location"))
        if output_location:
            if isfile(output_location):
                return
            elif not isdir(output_location):
                try:
                    makedirs(output_location)
                except:
                    pass
            output_location = ["-d", output_location]
        else:
            output_location = []
        if dependencies:
            classpath = ["-classpath", pathsep.join(dependencies)]
        else:
            classpath = []
        return [
            JDKManager().get_executable("lint") or "javac",
            "-sourcepath",
            sourcepath
        ] + classpath + output_location + [
            sublime.active_window().active_view().file_name(),
            Settings().get("linter_arguments", "")
        ]
