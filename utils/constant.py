import sublime
from ..core import (
    ActionHistory,
    PackagesManager,
    ProjectRestoration,
    Settings,
    SnippetsManager,
    StatusManager
)
from .timer import Timer


class Constant:

    """
    Collection of
     - things to be changed through out releases
     - frequently used functions
     - tiny functions
    """

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
    def settings_ready():
        return Settings.ready()

    @staticmethod
    def ready():
        return SnippetsManager.ready() and PackagesManager.ready()

    @staticmethod
    def startup():
        StatusManager.reset()
        ActionHistory.reset()
        Settings.reset()
        SnippetsManager.reset()
        PackagesManager.reset()

        ActionHistory.add_action("javatar", "Startup")
        Settings.startup()

        Timer.timer(reset=True)
        Constant.check_settings()

    @staticmethod
    def post_settings():
        StatusManager.pre_startup()
        ProjectRestoration.load_state()
        SnippetsManager.startup(on_done=PackagesManager.startup)

    @staticmethod
    def post_startup():
        StatusManager.startup()
        StatusManager.show_status("Javatar is ready")
        print("[Javatar] Startup Time: {0:.2f}s".format(Constant.startup_time))
        ActionHistory.add_action("javatar", "Ready within {0:.2f}s".format(Constant.startup_time))

    @staticmethod
    def check_startup():
        if Constant.ready():
            Constant.startup_time = Timer.timer(reset=True)
            Constant.post_startup()
        else:
            sublime.set_timeout(Constant.check_startup, 100)

    @staticmethod
    def check_settings():
        if Constant.settings_ready():
            Constant.post_settings()
            Constant.check_startup()
        else:
            sublime.set_timeout(Constant.check_settings, 100)

    @staticmethod
    def is_debug():
        return Settings.get("debug_mode", False)
