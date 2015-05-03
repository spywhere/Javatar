class _Logger:
    NONE = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    DEBUG = 4

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def reset(self):
        """
        Reset all changes (used on restart)

        This class use this method for nothing (for now)
        It just prepared for future uses (if any)
        """
        pass

    def startup(self):
        """
        Initialize required variables (if any)
        """
        from ..utils import Constant
        print("[Javatar] v%s" % (Constant.get_version()))

    def none(self, message):
        """
        Print a message
        """
        print("%s" % (str(message)))

    def debug(self, message):
        """
        Print a debug message
        """
        from ..utils import Constant
        if Constant.is_debug():
            print("[Javatar Debug] %s" % (str(message)))

    def info(self, message):
        """
        Print an informative message
        """
        print("[Javatar] %s" % (str(message)))

    def warning(self, message):
        """
        Print a warning message
        """
        print("[Javatar] Warning! %s" % (str(message)))

    def error(self, message):
        """
        Print an error message
        """
        print("[Javatar] Error! %s" % (str(message)))

    def log(self, message, level=None):
        """
        Print a message to console based on logging level
        """
        level = level or self.INFO
        if level == self.DEBUG:
            self.debug(message)
        elif level == self.INFO:
            self.info(message)
        elif level == self.WARNING:
            self.warning(message)
        elif level == self.ERROR:
            self.error(message)
        else:
            self.none(message)


def Logger():
    return _Logger.instance()
