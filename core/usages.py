import sublime
import os.path
from .action_history import ActionHistory
from .logger import Logger
from .settings import Settings
from ..utils import Constant, Downloader


class _Usages:
    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def send_usages(self):
        if Settings().get("send_stats_and_usages"):
            version = Settings().get_global("version")
            action = "install"
            if version and version == Constant.get_version():
                return
            elif version:
                action = "upgrade"
            params = self.get_usages_data()
            params["Action"] = action
            params["usage"] = "true"
            try:
                Downloader.request(
                    Constant.get_usages_host(),
                    params,
                    on_complete=self.on_usages_sent
                )
            except Exception as e:
                ActionHistory().add_action(
                    "javatar.core.usages.send_usages",
                    "Error while sending usages data",
                    e
                )

    def on_usages_sent(self, data):
        if "Finished" in data.decode():
            Logger().info("Javatar usages has been sent")
            Settings().set("version", Constant.get_version(), to_global=True)
        else:
            Logger().error("Failed to send Javatar usages informations: %s" % (
                data.decode()
            ))

    def get_usages_data(self):
        return {
            "SchemaVersion": Constant.get_usages_schema_version(),
            "Version": Constant.get_version(),
            "DebugMode": str.lower(str(Settings().get("debug_mode"))),
            "AsPackage": str.lower(str(os.path.exists(os.path.join(
                sublime.installed_packages_path(),
                "Javatar.sublime-package"
            )))),
            "StartupTime": "{0:.2f}s".format(Constant.startup_time),
            "ActionHistory": str.lower(str(
                Settings().get("enable_action_history")
            )),
            "SublimeVersion": str(sublime.version()),
            "Platform": sublime.platform(),
            "Architecture": sublime.arch()
        }

    def send_packages_usages(self):
        if Settings().get("send_stats_and_usages"):
            params = self.get_usages_data()
            params["package"] = "true"


def Usages():
    return _Usages.instance()
