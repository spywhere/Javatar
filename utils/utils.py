import sublime
import os.path


class Utils:

    """
    A collection of small functions
    """

    @staticmethod
    def to_readable_size(filesize, base=1000):
        """
        Convert a number into a readable file size

        @param filesize: a value to convert, if provided as a number
            if provided as a string, will thread as a file and
            will gather a file size for calculation
        @param base: a base value for calculation
            Decimal use 1000
            Binary use 1024
        """
        if isinstance(filesize, str):
            if filesize[:8] == "Packages":
                filesize = sublime.packages_path() + filesize[8:]
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
