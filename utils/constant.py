import sublime
import sys
from ..core import (
    ActionHistory,
    Logger,
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
        return "2.0.0-pre-alpha"

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
        return (
            "https://raw.github.com/spywhere/JavatarPackages/" +
            "master/javatar_packages.json"
        )

    @staticmethod
    def settings_ready():
        return Settings().ready()

    @staticmethod
    def ready():
        return SnippetsManager().ready() and PackagesManager().ready()

    @staticmethod
    def startup():
        Logger().reset()
        StatusManager().reset()
        ActionHistory().reset()
        Settings().reset()
        SnippetsManager().reset()
        PackagesManager().reset()

        ActionHistory().add_action("javatar", "Startup")
        Settings().startup()

        Timer.timer(reset=True)
        Constant.check_settings()

    @staticmethod
    def post_settings():
        Logger().startup()
        StatusManager().pre_startup()
        ProjectRestoration().load_state()
        SnippetsManager().startup(on_done=PackagesManager().startup)

    @staticmethod
    def post_startup():
        StatusManager().startup()
        Constant.check_conflicts(
            StatusManager().show_status("Javatar is ready")
        )
        Logger().info("Startup Time: {0:.2f}s".format(Constant.startup_time))
        ActionHistory().add_action(
            "javatar",
            "Ready within {0:.2f}s".format(Constant.startup_time)
        )

    @staticmethod
    def check_conflicts(old_ref=None):
        file_header = [
            mod
            for mod in sys.modules.keys()
            if mod.lower().startswith("fileheader")
        ]
        if file_header:
            message = (
                "FileHeader is installed. Javatar might conflicts with" +
                " FileHeader when create a new file"
            )
            StatusManager().hide_status(old_ref)
            Logger().warning(message)
            StatusManager().show_status(
                message,
                ref=old_ref,
                scrolling=StatusManager().SCROLL,
                delay=25000,
                must_see=True
            )

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
        return Settings().get("debug_mode", False)
