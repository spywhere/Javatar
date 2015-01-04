import sublime
from .action_history import ActionHistory
from .settings import Settings
from .timer import Timer


class Constant:
    @staticmethod
    def get_version():
        return "1.0.0dev"

    @staticmethod
    def get_usages_schema_version():
        return "1.0"

    @staticmethod
    def get_usages_host():
        return "http://javatar.digitalparticle.com/"

    @staticmethod
    def get_packages_schema_version():
        return "1.0"

    @staticmethod
    def get_packages_repo():
        return "https://raw.github.com/spywhere/JavatarPackages/master/javatar_packages.json"

    @staticmethod
    def ready():
        return Settings.ready()

    @staticmethod
    def reset():
        ActionHistory.reset()
        Settings.reset()
        # Reset snippets and packages

        Timer.timer(reset=True)
        Constant.check_startup()

    @staticmethod
    def check_startup():
        if Constant.ready():
            Constant.startup_time = Timer.timer(reset=True)
            print("[Javatar] Startup Time: {0:.2f}s".format(Constant.startup_time))
        else:
            sublime.set_timeout(Constant.check_startup, 100)

    @staticmethod
    def is_debug():
        return Settings.get("debug_mode", False)
