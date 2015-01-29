import sublime
from .action_history import ActionHistory
from .logger import Logger
from .thread_progress import ThreadProgress
from ..threads import (
    PackageInstallerThread,
    PackagesLoaderThread,
    PackagesUpdaterThread
)


class PackagesManager:

    """
    Load, store and install Javatar packages
    """

    @staticmethod
    def reset():
        """
        Resets all stored data
        """
        ActionHistory.add_action(
            "javatar.core.packages_manager.reset", "Reset all packages"
        )
        PackagesManager.installed_packages = None
        PackagesManager.default_packages = None

    @staticmethod
    def get_installed_packages(name=None):
        """
        Returns installed packages list or just one installed package

        @param name: if provided as None, will returns all installed packages
            otherwise, will returns package starts by specified name (if any)
        """
        if name is None:
            return PackagesManager.installed_packages or []
        else:
            for package in PackagesManager.get_installed_packages():
                if package["name"].startswith(name):
                    return package
            return None

    @staticmethod
    def on_packages_loaded(packages):
        """
        Callback after packages are loaded

        This method will update "Uninstall Packages..." menu

        @param packages: packages list informations
        """
        PackagesManager.installed_packages = packages["installed_packages"]
        PackagesManager.default_packages = packages["default_packages"]

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
        for package in PackagesManager.installed_packages:
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

    @staticmethod
    def startup(on_done=None):
        """
        Load packages

        @param on_done: callback after loaded
        """
        PackagesManager.load_packages(
            on_done=lambda: PackagesManager.update_packages_list(
                on_done=on_done
            )
        )

    @staticmethod
    def load_packages(on_done=None):
        """
        Load packages

        @param on_done: callback after loaded
        """
        ActionHistory.add_action(
            "javatar.core.packages_manager.load_packages", "Load packages"
        )
        thread = PackagesLoaderThread(PackagesManager.on_packages_loaded)
        ThreadProgress(
            thread, "Loading Javatar packages",
            "Javatar packages has been successfully loaded",
            on_done=on_done
        )

    @staticmethod
    def on_packages_list_updated(require_package):
        """
        Callback after packages list is updated

        This method will install required package (if specified)

        @param require_package: required package informations
        """
        if require_package is None:
            Logger.debug("Skip required package installation")
            return
        package_conflict = []
        if "conflict" in require_package:
            package_conflict = require_package["conflict"]
        for conflict in package_conflict:
            if PackagesManager.get_installed_packages(conflict) is not None:
                Logger.debug("Conflict package was already installed")
                ActionHistory.add_action(
                    "javatar.core.packages_manager.update_status",
                    "Conflict package was already installed"
                )
                return
        ActionHistory.add_action(
            "javatar.core.packages_manager.update_status",
            "Install required package"
        )

        Logger.debug("Starting required package installation")
        PackagesManager.install_package(require_package)

    @staticmethod
    def update_packages_list(no_install=False, on_done=None):
        """
        Update packages list

        @param no_install: if provided as True, will not install required
            packages after update a packages list
        @param on_done: callback after loaded
        """
        ActionHistory.add_action(
            "javatar.core.packages_manager.update_packages_list",
            "Update packages list"
        )
        thread = PackagesUpdaterThread(
            no_install,
            PackagesManager.on_packages_list_updated
        )
        ThreadProgress(
            thread, "Updating Javatar packages",
            "Javatar packages has been successfully updated",
            on_done=on_done
        )

    @staticmethod
    def on_package_installed(package, on_done=None):
        """
        Callback after package has been installed

        This method will refresh all package list again

        @param package: an installed package informations
        @param on_done: callback after refreshed
        """
        PackagesManager.reset()
        PackagesManager.load_packages(
            on_done=lambda: PackagesManager.update_packages_list(
                no_install=True,
                on_done=on_done
            )
        )

    @staticmethod
    def install_package(package, on_done=None):
        """
        Install specified Javatar's package

        @param package: a package informations
        @param on_done: callback after installed
        """
        ActionHistory.add_action(
            "javatar.core.packages_manager.install_package",
            "Install package [name=%s]" % (package["name"])
        )
        thread = PackageInstallerThread(
            package,
            lambda pkg: PackagesManager.on_package_installed(pkg, on_done)
        )
        ThreadProgress(
            thread,
            "Installing Javatar package \"%s\"" % (package["name"]),
            (
                "Javatar package \"%s\" has been " % (package["name"]) +
                "successfully installed"
            )
        )

    @staticmethod
    def ready():
        """
        Returns whether manager ready to be used
        """
        return (PackagesManager.installed_packages is not None and
                PackagesManager.default_packages is not None)
