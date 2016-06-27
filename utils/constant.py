import sublime
import sys
from ..core import (
    ActionHistory,
    HelperService,
    JDKManager,
    Logger,
    PluginManager,
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
        return "2.0.0-prebeta.6"

    @staticmethod
    def get_usages_schema_version():
        return "2.0"

    @staticmethod
    def get_usages_host():
        return "http://api.digitalparticle.com/1/stats/"

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
        return (
            JDKManager().ready() and
            SnippetsManager().ready()
        )

    @staticmethod
    def reset():
        JDKManager().reset()
        Logger().reset()
        StatusManager(True).reset()
        ActionHistory().reset()
        Settings().reset()
        SnippetsManager().reset()

    @staticmethod
    def startup():
        Constant.reset()
        ActionHistory().add_action("javatar", "Startup")
        Settings().startup()

        Timer.timer(reset=True)
        Constant.check_settings()

    @staticmethod
    def post_settings():
        JDKManager().startup()
        Logger().startup()
        StatusManager().pre_startup()
        ProjectRestoration().load_state()
        SnippetsManager().startup()
        HelperService().startup()

    @staticmethod
    def post_startup():
        from ..core import Usages
        StatusManager().startup()
        Constant.check_upgrade()
        Constant.check_conflicts(
            StatusManager().show_status("Javatar is ready")
        )
        Logger().info("Startup Time: {0:.2f}s".format(Constant.startup_time))
        Usages().send_usages()
        ActionHistory().add_action(
            "javatar",
            "Ready within {0:.2f}s".format(Constant.startup_time)
        )
        from ..extensions import JavatarMenu
        from ..extensions import JavatarProjectRestoration
        JavatarMenu
        JavatarProjectRestoration
        PluginManager().load_plugins()

    @staticmethod
    def check_upgrade():
        deprecated_key = [
            "run_command",
            "build_command"
        ]
        upgrade_key = [
            "dependencies_path",
            "run_location"
            "build_location",
            "build_output_location"
        ]
        upgradable_keys = [
            "project_dir",
            "source_folder",
            "packages_path",
            "sep",
            "$"
        ]
        deprecated_keys = [key for key in deprecated_key if Settings().has(key)]
        upgrade_keys = []
        for key in upgrade_key:
            if Settings().has(key):
                value = Settings().get(key)
                for k in upgradable_keys:
                    if ("$" + k) in value:
                        upgrade_keys.append(key)
                        break
        if deprecated_keys:
            Logger().warning(
                "Your settings contain deprecated key." +
                " Please consider changing your \"" +
                ", ".join(deprecated_keys) +
                "\" key to a new one."
            )
        if upgrade_keys:
            do_upgrade = sublime.ok_cancel_dialog(
                "Your Javatar's settings contain old version of macro system" +
                " setttings.\n\nDo you want Javatar to upgrade the upgradable" +
                " settings for you?",
                "Upgrade"
            )
            if do_upgrade:
                Settings().upgrade_settings(upgrade_keys)
                sublime.message_dialog(
                    "Javatar's settings have been upgraded." +
                    " Please validate the settings before continue your work."
                )

    @staticmethod
    def check_conflicts(old_ref=None):
        file_header = [
            mod
            for mod in sys.modules.keys()
            if mod.lower().startswith("fileheader")
        ]
        sublime_linter = [
            mod
            for mod in sys.modules.keys()
            if mod.lower().startswith("sublimelinter")
        ]
        message = ""
        if sublime_linter:
            from ..extensions.linter import JavatarLinter
            JavatarLinter
            Logger().info(
                "SublimeLinter is installed. Javatar linter now enabled"
            )
        else:
            message += ("SublimeLinter is not installed." +
                        " Javatar linter now disabled")
        if file_header:
            msg = (
                "FileHeader is installed. Javatar might conflicts with" +
                " FileHeader when create a new file"
            )
            if message:
                message += "    "
            message += msg
            Logger().warning(msg)
        StatusManager().hide_status(old_ref)
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
