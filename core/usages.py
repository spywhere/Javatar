import sublime
import os.path
import traceback
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
            params = self.get_usages_data()
            params["usage"] = "true"
            try:
                Downloader.request(
                    Constant.get_usages_host(),
                    params,
                    on_complete=self.on_usages_sent
                )
            except:
                Logger().error(
                    "Error while sending usages data\n%s" % (
                        traceback.format_exc()
                    )
                )

    def on_usages_sent(self, data):
        Logger().info("Javatar usages has been sent")

    def get_usages_data(self):
        return {
            "SchemaVersion": Constant.get_usages_schema_version(),
            "JavatarVersion": Constant.get_version(),
            "JavatarDebugMode": str.lower(str(Settings().get("debug_mode"))),
            "JavatarAsPackage": str.lower(str(os.path.exists(os.path.join(
                sublime.installed_packages_path(),
                "Javatar.sublime-package"
            )))),
            "JavatarStartupTime": "{0:.2f}s".format(Constant.startup_time),
            "JavatarActionHistory": str.lower(str(
                Settings().get("enable_action_history")
            )),
            "SublimeVersion": str(sublime.version()),
            "Platform": sublime.platform(),
        }

    def send_packages_usages(self):
        if Settings().get("send_stats_and_usages"):
            params = self.get_usages_data()
            params["package"] = "true"
            # Downloader.request(
            #     Constant.get_usages_host(),
            #     params,
            #     on_complete=self.on_usages_sent
            # )


def Usages():
    return _Usages.instance()
