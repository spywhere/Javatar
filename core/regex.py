import re
from .settings import Settings


class _RE:

    """
    Regular Expressions wrapper
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.patterns = {}

    def get(self, pattern_key, pattern=None):
        """
        Returns a compiled regular expression pattern, if not compiled,
            otherwise, a cached pattern

        @param pattern_key: a regular expression pattern key to search in
            the settings
        @param pattern: a regular expression pattern
            if provided, will be used as a pattern instead of searching from
                settings
        """
        if pattern_key not in RE().patterns:
            pattern = pattern or Settings().get(pattern_key, default=None)
            if pattern is None:
                return None
            RE().patterns[pattern_key] = re.compile(pattern)
        return RE().patterns[pattern_key]

    def search(self, pattern_key, *args):
        """
        Returns a pattern searched result

        @param pattern_key: regular expression pattern key to search in
            the settings
        @param args: overloading arguments for a search function
        """
        pattern = RE().get(pattern_key)
        if pattern is None:
            return None
        return pattern.search(*args)

    def match(self, pattern_key, *args):
        """
        Returns a pattern matched result

        @param pattern_key: regular expression pattern key to match in
            the settings
        @param args: overloading arguments for a match function
        """
        pattern = RE().get(pattern_key)
        if pattern is None:
            return None
        return pattern.match(*args)

    def sub(self, pattern_key, *args):
        """
        Returns a pattern substituted result

        @param pattern_key: regular expression pattern key to substitute in
            the settings
        @param args: overloading arguments for a substitute function
        """
        pattern = RE().get(pattern_key)
        if pattern is None:
            return None
        return pattern.sub(*args)


def RE():
    return _RE.instance()
