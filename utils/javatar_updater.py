import sublime
import threading
import urllib.request
import hashlib
from .javatar_collections import *
from .javatar_thread import *
from .javatar_utils import *

# Alert if packages repo is out of date (new key for channel)

PACKAGES_VERSION = "0.3"
PACKAGES_REPO = "https://raw.github.com/spywhere/JavatarPackages/master/javatar_packages.json"


def updatePackages():
	getAction().addAction("javatar.util.updater", "Check packages update")
	thread = JavatarPackageUpdaterThread(updateComplete)
	thread.start()
	ThreadProgress(thread, "Checking Javatar packages", "Javatar packages has been successfully updated")


def updateComplete(packageURL, require_package):
	if require_package is None:
		return
	package_conflict = []
	if "conflict" in require_package:
		package_conflict = require_package["conflict"]
	for conflict in package_conflict:
		if getInstalledPackage(conflict) is not None:
			# Conflict package was already installed
			getAction().addAction("javatar.util.updater", "Conflict package was installed")
			return
	getAction().addAction("javatar.util.updater", "Install default package")
	sublime.active_window().run_command("javatar_install", {"installtype": "remote_package", "name": require_package["name"], "filename": require_package["filename"], "url": packageURL, "checksum": require_package["hash"], "conflict": package_conflict})


class JavatarPackageUpdaterThread(threading.Thread):
	def __init__(self, on_complete = None):
		self.on_complete = on_complete
		threading.Thread.__init__(self)

	def run(self):
		try:
			self.result_message = "Javatar packages update has been corrupted"
			urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()))
			data = urllib.request.urlopen(PACKAGES_REPO).read()
			datahash = hashlib.sha256(data).hexdigest()
			packages = sublime.decode_value(data.decode("utf-8"))

			global PACKAGES_LIST
			PACKAGES_LIST = []
			menu = {
				"selected_index": 1,
				"items": [["Back", "Back to previous menu"]],
				"actions": [
					{
						"name": "package_manager"
					}
				]
			}

			# Remote packages
			if PACKAGES_VERSION in packages:
				packageURL = ""
				if "url" in packages[PACKAGES_VERSION]:
					packageURL = packages[PACKAGES_VERSION]["url"]
				else:
					self.result_message = "No URL to packages channel"
					getAction().addAction("javatar.util.updater", self.result_message)
					self.result = False
					return
				require_package = None
				require_package_name = None
				if "packages" in packages[PACKAGES_VERSION]:
					remote_update = False
					if "install" in packages[PACKAGES_VERSION]:
						require_package_name = packages[PACKAGES_VERSION]["install"]
					for package in packages[PACKAGES_VERSION]["packages"]:
						remote_update = True
						if "name" in package and "filesize" in package and "filename" in package and "hash" in package and getInstalledPackage(package["name"]) is None and ("available" not in package or package["available"]):
							package_status = "Ready to download (~" + package["filesize"] + ")."
							package_conflict = []
							if "conflict" in package:
								package_conflict = package["conflict"]
							conflict_with = None
							for conflict in package_conflict:
								conflict_package = getInstalledPackage(conflict)
								if conflict_package is not None:
									# Conflict package was already installed
									conflict_with = conflict_package["name"]
									break
							if require_package_name is not None and package["name"] == require_package_name:
								require_package = package
							if conflict_with is None:
								menu["items"].append([package["name"], package_status])
								menu["actions"].append({"command": "javatar_install", "args": {"installtype": "remote_package", "name": package["name"], "filename": package["filename"], "url": packageURL, "checksum": package["hash"]}})
							else:
								menu["items"].append([package["name"], "Conflicted with \"" + conflict_with + "\""])
								menu["actions"].append({"name": "install_packages"})
					if remote_update:
						menu["selected_index"] = 2
						sublime.active_window().run_command("javatar", {"replaceMenu": {
						"name": "install_packages",
						"menu": menu
						}})
					self.result = True
					if self.on_complete is not None:
						sublime.set_timeout(lambda: self.on_complete(packageURL, require_package), 3000)
				else:
					self.result_message = "No Javatar packages available"
					getAction().addAction("javatar.util.updater", self.result_message)
					self.result = False
			else:
				self.result_message = "Javatar packages are incompatible with current version"
				getAction().addAction("javatar.util.updater", self.result_message)
				self.result = False
		except Exception as e:
			self.result_message = "Javatar packages update has failed: "+ str(e)
			getAction().addAction("javatar.util.updater", self.result_message)
			self.result = False
