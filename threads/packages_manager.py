import sublime
import threading
from os.path import basename, join
from ..core import (
    ActionHistory,
    Logger
)


class PackageInstallerThread(threading.Thread):

    """
    A thread to install packages
    """

    def __init__(self, package, on_complete=None):
        self.package = package
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def on_downloaded(self, data):
        """
        Install the package if data is found

        @param data: data to check
        """
        if data is None:
            self.result_message = (
                "Javatar package \"%s\" " % (self.package["name"]) +
                "has been corrupted"
            )
            self.result = False
            return
        self.result = True
        if self.on_complete is not None:
            sublime.set_timeout(
                lambda: self.on_complete(self.package),
                3000
            )

    def run(self):
        """
        Download and install the specified package
        """
        try:
            from ..utils import Downloader
            local_path = join(
                sublime.packages_path(),
                "User",
                "%s.javatar-packages" % (self.package["filename"])
            )
            self.package["local_path"] = local_path
            Downloader.download_file(
                url="%s.javatar-packages" % (self.package["url"]),
                path=local_path,
                checksum=self.package["hash"],
                on_complete=self.on_downloaded
            )
        except Exception as e:
            self.result_message = (
                "Javatar package \"%s\" " % (self.package["name"]) +
                "installation has failed: %s" % (str(e))
            )
            ActionHistory().add_action(
                "javatar.core.package_installer",
                "Javatar package installation has failed", e
            )
            self.result = False


class PackagesLoaderThread(threading.Thread):

    """
    A thread to load all installed packages
    """

    def __init__(self, on_complete=None):
        self.installed_packages = []
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def count_classes(self, packages):
        """
        Returns a total amount of Java packages and classes from Javatar
            packages

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

        @param filename: a path to package file
        """
        try:
            packages = sublime.decode_value(sublime.load_resource(filepath))
        except ValueError as e:
            ActionHistory().add_action(
                "javatar.core.packages_loader_thread.analyse_package",
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
            Logger().log(
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
            ActionHistory().add_action(
                "javatar.core.packages_loader_thread.analyse_package",
                "Analyse package [file=" + filepath + "]"
            )
            packages = self.analyse_package(filepath)
            if packages:
                ActionHistory().add_action(
                    "javatar.core.packages_loader_thread.load_status",
                    "Javatar package " + filename + " loaded [file=" +
                    filepath + "]"
                )
                default_packages.append(packages)
            else:
                ActionHistory().add_action(
                    "javatar.core.packages_loader_thread.load_status",
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

    """
    A thread to refresh all package menus
    """

    def __init__(self, no_install=False, on_complete=None):
        self.no_install = no_install
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def contains_keys(self, obj, keys):
        """
        Returns whether an object contains specified keys

        @param obj: an object to be checked
        @param keys: a list of keys
        """
        return [x for x in obj if x in keys]

    def fetch_packages_data(self):
        """
        Returns a raw data from a Javatar packages repository
        """
        from ..utils import Constant, Downloader
        try:
            return sublime.decode_value(
                Downloader.download(
                    url=Constant.get_packages_repo()
                ).decode("utf-8")
            )
        except Exception as e:
            ActionHistory().add_action(
                (
                    "javatar.threads.packages_manager" +
                    ".PackagesUpdaterThread.fetch_packages_data"
                ),
                "Error while fetching packages data",
                e
            )
            return None

    def validate_packages(self, data):
        """
        Returns a package url if data is a valid Javatar package repository
        """
        from ..utils import Constant
        if Constant.get_packages_schema_version() not in data:
            self.result_message = ("Javatar packages are incompatible"
                                   + " with current version")
            ActionHistory().add_action(
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
            ActionHistory().add_action(
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
            ActionHistory().add_action(
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
            if not data:
                self.result_message = (
                    "Javatar packages update has failed:" +
                    " Cannot fetch packages data"
                )
                ActionHistory().add_action(
                    "javatar.core.packages_updater",
                    "Javatar packages update has failed"
                )
                self.result = False
                return
            if Constant.get_packages_schema_version() not in data:
                self.result_message = (
                    "Javatar packages update has failed: No schema %s" % (
                        Constant.get_packages_schema_version()
                    )
                )
                ActionHistory().add_action(
                    "javatar.core.packages_updater",
                    "Javatar packages update has failed"
                )
                self.result = False
                return
            packages = data[Constant.get_packages_schema_version()]
            package_url = self.validate_packages(data)
            if package_url is None:
                self.result = False
                return

            require_package = None
            require_package_name = None

            remote_update = False
            Logger().debug(
                "Bypass required package: " + str(self.no_install)
            )
            if not self.no_install and "install" in packages:
                require_package_name = packages["install"]

            from ..core import PackagesManager
            for package in packages["packages"]:
                remote_update = True
                if (self.contains_keys(package,
                                       ["name", "filesize",
                                       "filename", "hash"]) and
                    PackagesManager().get_installed_packages(
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
                        conflict_package = PackagesManager().get_installed_packages(
                            conflict
                        )
                        if conflict_package is not None:
                            # Conflict package was already installed
                            conflict_with = conflict_package["name"]
                            continue
                    package["url"] = package_url+package["filename"]
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
                                    "url": package["url"],
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
                    lambda: self.on_complete(require_package),
                    3000
                )

        except Exception as e:
            self.result_message = (
                "Javatar packages update has failed: " + str(e)
            )
            ActionHistory().add_action(
                "javatar.core.packages_updater",
                "Javatar packages update has failed", e
            )
            self.result = False
