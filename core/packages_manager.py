import sublime
from .action_history import ActionHistory
from .logger import Logger
from .thread_progress import ThreadProgress
from ..threads import (
    PackageInstallerThread,
    PackagesLoaderThread,
    PackagesUpdaterThread
)


class _PackagesManager:

    """
    Load, store and install Javatar packages
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.reset(silent=True)

    def reset(self, silent=False):
        """
        Resets all stored data
        """
        if not silent:
            ActionHistory().add_action(
                "javatar.core.packages_manager.reset", "Reset all packages"
            )
        self.installed_packages = None
        self.default_packages = None

    def get_packages(self):
        """
        Returns a list of loaded packages
        """
        return self.default_packages

    def get_installed_packages(self, name=None):
        """
        Returns installed packages list or just one installed package

        @param name: a package name filter
            if provided as None, will returns all installed packages

            otherwise, will returns package starts by specified name (if any)
        """
        if name is None:
            return self.installed_packages or []
        else:
            for package in self.get_installed_packages():
                if package["name"].startswith(name):
                    return package
            return None

    def types_in_package(self, package):
        """
        Returns a list of types in specified package

        @param package: a package retrieved from Packages Manager
        """
        types = []
        search_types = [
            "interface", "class", "enum", "exception", "error", "type",
            "annotation"
        ]
        for search_type in search_types:
            if search_type in package:
                types.extend(
                    class_info["name"]
                    for class_info in package[search_type]
                )
        return types

    def on_packages_loaded(self, packages):
        """
        Callback after packages are loaded

        This method will update "Uninstall Packages..." menu

        @param packages: packages list informations
        """
        self.installed_packages = packages["installed_packages"]
        self.default_packages = packages["default_packages"]

        installed_menu = {
            "selected_index": 1,
            "items": [["Back", "Back to previous menu"]],
            "actions": [
                {
                    "name": "package_manager"
                }
            ]
        }
        # Installed packages
        install_update = False
        from ..utils import Utils
        for package in self.installed_packages:
            install_update = True
            installed_menu["actions"] += [{
                "command": "javatar_install",
                "args": {
                    "installtype": "uninstall_package",
                    "name": package["name"],
                    "filename": package["path"]
                }
            }]
            installed_menu["items"] += [[
                package["name"],
                "Installed (" + Utils.to_readable_size(
                    package["path"]
                ) + ")."
            ]]
        if install_update:
            installed_menu["selected_index"] = 2
            sublime.active_window().run_command(
                "javatar", {
                    "replaceMenu": {
                        "name": "uninstall_packages",
                        "menu": installed_menu
                    }
                }
            )

    def startup(self, on_done=None):
        """
        Load packages

        @param on_done: callback after loaded
        """
        self.load_packages(
            on_done=lambda: self.update_packages_list(
                on_done=on_done
            )
        )

    def load_packages(self, on_done=None):
        """
        Load packages

        @param on_done: callback after loaded
        """
        ActionHistory().add_action(
            "javatar.core.packages_manager.load_packages", "Load packages"
        )
        thread = PackagesLoaderThread(self.on_packages_loaded)
        ThreadProgress(
            thread, "Loading Javatar packages",
            "Javatar packages has been successfully loaded",
            on_done=on_done
        )

    def on_packages_list_updated(self, require_package):
        """
        Callback after packages list is updated

        This method will install required package (if specified)

        @param require_package: required package informations
        """
        if require_package is None:
            Logger().debug("Skip required package installation")
            return
        package_conflict = []
        if "conflict" in require_package:
            package_conflict = require_package["conflict"]
        for conflict in package_conflict:
            if self.get_installed_packages(conflict) is not None:
                Logger().debug("Conflict package was already installed")
                ActionHistory().add_action(
                    "javatar.core.packages_manager.update_status",
                    "Conflict package was already installed"
                )
                return
        ActionHistory().add_action(
            "javatar.core.packages_manager.update_status",
            "Install required package"
        )

        Logger().debug("Starting required package installation")
        self.install_package(require_package)

    def update_packages_list(self, no_install=False, on_done=None):
        """
        Update packages list

        @param no_install: a boolean specified whether not install required
            packages after update a packages list or not
        @param on_done: callback after loaded
        """
        ActionHistory().add_action(
            "javatar.core.packages_manager.update_packages_list",
            "Update packages list"
        )
        thread = PackagesUpdaterThread(
            no_install,
            self.on_packages_list_updated
        )
        ThreadProgress(
            thread, "Updating Javatar packages",
            "Javatar packages has been successfully updated",
            on_done=on_done
        )

    def on_package_installed(self, package, on_done=None):
        """
        Callback after package has been installed

        This method will refresh all package list again

        @param package: an installed package informations
        @param on_done: callback after refreshed
        """
        # TODO(spywhere): Send packages usages
        self.reset()
        self.load_packages(
            on_done=lambda: self.update_packages_list(
                no_install=True,
                on_done=on_done
            )
        )

    def install_package(self, package, on_done=None):
        """
        Install specified Javatar's package

        @param package: a package informations
        @param on_done: callback after installed
        """
        ActionHistory().add_action(
            "javatar.core.packages_manager.install_package",
            "Install package [name=%s]" % (package["name"])
        )
        thread = PackageInstallerThread(
            package,
            lambda pkg: self.on_package_installed(pkg, on_done)
        )
        ThreadProgress(
            thread,
            "Installing Javatar package \"%s\"" % (package["name"]),
            (
                "Javatar package \"%s\" has been " % (package["name"]) +
                "successfully installed"
            )
        )

    def ready(self):
        """
        Returns whether manager ready to be used
        """
        return (self.installed_packages is not None and
                self.default_packages is not None)


def PackagesManager():
    return _PackagesManager.instance()
