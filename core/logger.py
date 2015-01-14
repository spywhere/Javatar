class Logger:
    NONE = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    DEBUG = 4

    @staticmethod
    def reset():
        """
        Reset all changes (used on restart)

        This class use this method for nothing (for now)
        It just prepared for future uses (if any)
        """
        pass

    @staticmethod
    def startup():
        """
        Initialize required variables (if any)
        """
        from ..utils import Constant
        print("[Javatar] v%s" % (Constant.get_version()))

    @staticmethod
    def none(message):
        """
        Print a message
        """
        print("%s" % (str(message)))

    @staticmethod
    def debug(message):
        """
        Print a debug message
        """
        from ..utils import Constant
        if Constant.is_debug():
            print("[Javatar Debug] %s" % (str(message)))

    @staticmethod
    def info(message):
        """
        Print an informative message
        """
        print("[Javatar] %s" % (str(message)))

    @staticmethod
    def warning(message):
        """
        Print a warning message
        """
        print("[Javatar] Warning! %s" % (str(message)))

    @staticmethod
    def error(message):
        """
        Print an error message
        """
        print("[Javatar] Error! %s" % (str(message)))

    @staticmethod
    def log(message, level=None):
        """
        Print a message to console based on logging level
        """
        level = level or Logger.INFO
        if level == Logger.DEBUG:
            Logger.debug(message)
        elif level == Logger.INFO:
            Logger.info(message)
        elif level == Logger.WARNING:
            Logger.warning(message)
        elif level == Logger.ERROR:
            Logger.error(message)
        else:
            Logger.none(message)
