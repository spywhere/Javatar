import sublime
import threading
import urllib
from os.path import basename
from .action_history import ActionHistory
from .logger import Logger
from .thread_progress import ThreadProgress


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
            return PackagesManager.installed_packages
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
            on_done=lambda: PackagesManager.update_packages(on_done=on_done)
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
        thread = PackagesManagerThread(PackagesManager.on_packages_loaded)
        ThreadProgress(
            thread, "Loading Javatar packages",
            "Javatar packages has been successfully loaded",
            on_done=on_done
        )

    @staticmethod
    def on_packages_updated(package_url, require_package):
        """
        Callback after packages are updated

        This method will install required package (if specified)

        @param package_url: url to download package file
        @param require_package: required package informations
        """
        if require_package is None:
            return
        package_conflict = []
        if "conflict" in require_package:
            package_conflict = require_package["conflict"]
        for conflict in package_conflict:
            if PackagesManager.get_installed_packages(conflict) is not None:
                ActionHistory.add_action(
                    "javatar.core.packages_manager.update_status",
                    "Conflict package was already installed"
                )
                return
        ActionHistory.add_action(
            "javatar.core.packages_manager.update_status",
            "Install required package"
        )
        sublime.active_window().run_command(
            "javatar_install",
            {
                "installtype": "remote_package",
                "name": require_package["name"],
                "filename": require_package["filename"],
                "url": package_url,
                "checksum": require_package["hash"]
            }
        )

    @staticmethod
    def update_packages(no_install=False, on_done=None):
        """
        Update packages

        @param no_install: if provided as True, will not install required
            packages after update a packages list
        @param on_done: callback after loaded
        """
        ActionHistory.add_action(
            "javatar.core.packages_manager.update_packages",
            "Update packages list"
        )
        thread = PackagesUpdaterThread(no_install,
                                       PackagesManager.on_packages_updated)
        ThreadProgress(
            thread, "Updating Javatar packages",
            "Javatar packages has been successfully updated",
            on_done=on_done
        )

    @staticmethod
    def ready():
        """
        Returns whether manager ready to be used
        """
        return (PackagesManager.installed_packages is not None and
                PackagesManager.default_packages is not None)


class PackagesManagerThread(threading.Thread):
    def __init__(self, on_complete=None):
        self.installed_packages = []
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def count_classes(self, packages):
        """
        Returns total amount of Java packages and classes from Javatar packages

        @param packages: Javatar packages informations
        """
        total_packages = 0
        total_classes = 0

        keys = {
            "interface",
            "class",
            "enum",
            "exception",
            "error",
            "annotation",
            "type"
        }

        if "packages" in packages:
            for packageName in packages["packages"]:
                package = packages["packages"][packageName]
                total_packages += 1

                for key in keys:
                    if key in package:
                        total_classes += len(package[key])

        return [total_packages, total_classes]

    def analyse_package(self, filepath):
        """
        Analyse package source and returns package informations

        @param filename: path to package file
        """
        try:
            packages = sublime.decode_value(sublime.load_resource(filepath))
        except ValueError as e:
            ActionHistory.add_action(
                "javatar.core.packages_manager_thread.analyse_package",
                "Invalid JSON package [file=" + filepath + "]",
                e
            )
        else:
            if "experiment" in packages and packages["experiment"]:
                return None
            filename = basename(filepath)
            if "name" in packages:
                filename = packages["name"]
            count = self.count_classes(packages)
            self.installed_packages.append({"name": filename,
                                            "path": filepath})
            Logger.log(
                'Package "{}" loaded with {} classes in {} packages'
                .format(
                    filename,
                    count[1],
                    count[0]
                )
            )
            return packages

        return None

    def run(self):
        """
        Search for all packages and load them
        """
        default_packages = []
        for filepath in sublime.find_resources("*.javatar-packages"):
            filename = basename(filepath)
            ActionHistory.add_action(
                "javatar.core.packages_manager_thread.analyse_package",
                "Analyse package [file=" + filepath + "]"
            )
            packages = self.analyse_package(filepath)
            if packages:
                ActionHistory.add_action(
                    "javatar.core.packages_manager_thread.load_status",
                    "Javatar package " + filename + " loaded [file=" +
                    filepath + "]"
                )
                default_packages.append(packages)
            else:
                ActionHistory.add_action(
                    "javatar.core.packages_manager_thread.load_status",
                    "Javatar package load failed [file=" + filepath + "]"
                )

        data = {
            "installed_packages": self.installed_packages,
            "default_packages": default_packages
        }
        self.result = True
        if self.on_complete is not None:
            sublime.set_timeout(lambda: self.on_complete(data), 10)


class PackagesUpdaterThread(threading.Thread):

    def __init__(self, no_install=False, on_complete=None):
        self.no_install = no_install
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def contains_keys(self, obj, keys):
        """
        Returns whether object contains specified keys

        @param obj: object to be checked
        @param keys: a list of keys
        """
        return [x for x in obj if x in keys]

    def fetch_packages_data(self):
        """
        Returns raw data from Javatar packages repository
        """
        from ..utils import Constant
        urllib.request.install_opener(
            urllib.request.build_opener(urllib.request.ProxyHandler()))
        rawdata = urllib.request.urlopen(Constant.get_packages_repo()).read()
        return sublime.decode_value(rawdata.decode("utf-8"))

    def validate_packages(self, data):
        """
        Returns packages url if data is valid Javatar packages repository
        """
        from ..utils import Constant
        if Constant.get_packages_schema_version() not in data:
            self.result_message = ("Javatar packages are incompatible"
                                   + " with current version")
            ActionHistory.add_action(
                "javatar.core.packages_updater.validate_packages",
                self.result_message
            )
            return None

        packages = data[Constant.get_packages_schema_version()]
        package_url = None
        if "url" in packages:
            package_url = packages["url"]
        else:
            self.result_message = "No URL to packages channel"
            ActionHistory.add_action(
                "javatar.core.packages_updater.validate_packages",
                self.result_message
            )
            return None

        if "deprecated" in packages and packages["deprecated"]:
            self.result_message = ("Javatar is out of date."
                                   + " You must update Javatar"
                                   + " to get latest packages updates.")
            return None

        if "packages" not in packages:
            self.result_message = "No Javatar packages available"
            ActionHistory.add_action(
                "javatar.core.packages_updater.validate_packages",
                self.result_message
            )
            return None
        return package_url

    def run(self):
        """
        Update "Install Packages..." menu
        """
        try:
            from ..utils import Constant
            self.result_message = "Javatar packages update has been corrupted"
            menu = {
                "selected_index": 1,
                "items": [["Back", "Back to previous menu"]],
                "actions": [
                    {
                        "name": "package_manager"
                    }
                ]
            }

            data = self.fetch_packages_data()
            packages = data[Constant.get_packages_schema_version()]
            package_url = self.validate_packages(data)
            if package_url is None:
                self.result = False
                return

            require_package = None
            require_package_name = None

            remote_update = False
            Logger.debug(
                "Install required package: " + str(self.no_install)
            )
            if not self.no_install and "install" in packages:
                require_package_name = packages["install"]

            for package in packages["packages"]:
                remote_update = True
                if (self.contains_keys(package,
                                       ["name", "filesize",
                                       "filename", "hash"]) and
                    PackagesManager.get_installed_packages(
                        package["name"]
                    ) is None and
                        ("available" not in package or package["available"])):

                    package_status = ("Ready to download (~" +
                                      package["filesize"] + ").")
                    package_conflict = []
                    if "conflict" in package:
                        package_conflict = package["conflict"]
                    conflict_with = None
                    for conflict in package_conflict:
                        conflict_package = PackagesManager.get_installed_packages(
                            conflict
                        )
                        if conflict_package is not None:
                            # Conflict package was already installed
                            conflict_with = conflict_package["name"]
                            break
                    if (require_package_name is not None and
                            package["name"] == require_package_name):
                        require_package = package
                    if conflict_with is None:
                        menu["items"].append([package["name"], package_status])
                        menu["actions"].append(
                            {
                                "command": "javatar_install",
                                "args": {
                                    "installtype": "remote_package",
                                    "name": package["name"],
                                    "filename": package["filename"],
                                    "url": package_url,
                                    "checksum": package["hash"]
                                }
                            }
                        )
                    else:
                        menu["items"].append(
                            [
                                package["name"],
                                "Conflicted with \"" + conflict_with + "\""
                            ]
                        )
                        menu["actions"].append({"name": "install_packages"})
            if remote_update:
                menu["selected_index"] = 2
                sublime.active_window().run_command(
                    "javatar",
                    {
                        "replaceMenu": {
                            "name": "install_packages",
                            "menu": menu
                        }
                    }
                )
            self.result = True
            if self.on_complete is not None:
                sublime.set_timeout(
                    lambda: self.on_complete(
                        package_url,
                        require_package
                    ), 3000)

        except Exception as e:
            self.result_message = (
                "Javatar packages update has failed: " + str(e)
            )
            ActionHistory.add_action(
                "javatar.core.packages_updater",
                "Javatar packages update has failed", e
            )
            self.result = False
