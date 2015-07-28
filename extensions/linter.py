import sublime
from os import pathsep
from ..core import (
    DependencyManager,
    JDKManager,
    StateProperty,
    Settings
)
from SublimeLinter.lint import Linter, util


class JavatarLinter(Linter):
    """Provides an interface to javac."""

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
        Return the command line to execute.
        We override this because we have to munge the -Xlint argument
        based on the "lint" setting.
        """

        sourcepath = pathsep.join(StateProperty().get_source_folders())
        dependencies = StateProperty().get_source_folders() + [
            dependency[0]
            for dependency
            in DependencyManager().get_dependencies()
        ]
        classpath = pathsep.join(dependencies)

        return (
            JDKManager().get_executable("lint"),
            "-sourcepath",
            sourcepath,
            "-classpath",
            classpath,
            sublime.active_window().active_view().file_name(),
            Settings().get("linter_arguments", "")
        )
