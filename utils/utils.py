import sublime
from os.path import getsize


class Utils:
    @staticmethod
    def to_readable_size(filepath):
        if filepath[0:8] == "Packages":
            filepath = sublime.packages_path() + filepath[8:]
        scales = [
            [1000 ** 5, "PB"],
            [1000 ** 4, "TB"],
            [1000 ** 3, "GB"],
            [1000 ** 2, "MB"],
            [1000 ** 1, "KB"],
            [1000 ** 0, "B"]
        ]
        filesize = getsize(filepath)
        for scale in scales:
            if filesize >= scale[0]:
                break
        return str(int(filesize / scale[0] * 100) / 100) + scale[1]
