import sublime
import re
import os.path


class Utils:

    """
    A collection of small functions
    """

    @staticmethod
    def time_from_string(time_str):
        duration = 0
        match = re.match(
            (
                "((?P<day>\\d+)d)?((?P<hour>\\d+)h)?" +
                "((?P<min>\\d+)m)?((?P<sec>\\d+)s)?"
            ), time_str
        )
        if match:
            if match.group("day"):
                duration += int(match.group("day")) * 8640
            if match.group("hour"):
                duration += int(match.group("hour")) * 3600
            if match.group("min"):
                duration += int(match.group("min")) * 60
            if match.group("sec"):
                duration += int(match.group("sec"))
        return duration

    @staticmethod
    def to_readable_size(filesize, base=1000):
        """
        Converts a number into a readable file size

        @param filesize: a value to convert, if provided as a number
            if provided as a string, will thread as a file and
            will gather a file size for calculation
        @param base: a base value for calculation
            Decimal use 1000
            Binary use 1024
        """
        if isinstance(filesize, str):
            if filesize[:9] == "Packages/":
                filesize = os.path.join(sublime.packages_path(), filesize[9:])
            return Utils.to_readable_size(os.path.getsize(filesize), base)
        scales = [
            [base ** 5, "PB"],
            [base ** 4, "TB"],
            [base ** 3, "GB"],
            [base ** 2, "MB"],
            [base ** 1, "kB"],
            [base ** 0, "B"]
        ]
        for scale in scales:
            if filesize >= scale[0]:
                break
        return "%.2f%s" % (filesize / scale[0], scale[1])

    @staticmethod
    def split_path(path):
        """
        Splits a path into path components

        @param path: path to split
        """
        rest, tail = os.path.split(path)
        if len(rest) == 0:
            return (tail,)
        return Utils.split_path(rest) + (tail,)

    @staticmethod
    def contains_file(directory, file_path):
        """
        Checks if a directory contains specified file

        @param directory: a directory path to be checked
        @param file_path: a file path
        """
        return os.path.normcase(os.path.normpath(file_path)).startswith(
            os.path.normcase(os.path.normpath(directory))
        )
