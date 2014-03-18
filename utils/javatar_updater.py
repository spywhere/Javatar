


import sublime
import threading
import urllib.request
import hashlib
from .javatar_collections import *
from .javatar_thread import *
from .javatar_utils import *

PACKAGES_VERSION = "0.2"
PACKAGES_REPO = "https://raw.github.com/spywhere/JavatarPackages/master/javatar_packages.json"


def updatePackages():
	getAction().addAction("javatar.util.updater", "Check packages update")
	thread = JavatarPackageUpdaterThread()
	thread.start()
	ThreadProgress(thread, "Checking Javatar packages", "Javatar packages has been successfully updated")


class JavatarPackageUpdaterThread(threading.Thread):
	def __init__(self):
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
				"items": [["Back", "Back to previous menu"], ["Reload and Update packages", "Reload all pacakges and update packages list"]],
				"actions": [
					{
						"name": "help"
					}, {
						"command": "javatar_reload_packages"
					}
				]
			}

			if "packages" in packages and "version" in packages:
				if packages["version"] != PACKAGES_VERSION:
					self.result_message = "Javatar packages are incompatible with current version"
					getAction().addAction("javatar.util.updater", self.result_message)
					self.result = False
					return
				packageURL = ""
				if "url" in packages:
					packageURL = packages["url"]
				for package in packages["packages"]:
					if "name" in package and "filename" in package and "details" in package and "hash" in package and package["name"] not in getInstalledPackages():
						menu["selected_index"] = 3
						menu["items"].append([package["name"], package["details"]])
						menu["actions"].append({"command": "javatar_install", "args": {"installtype": "remote_package", "name": package["name"], "filename": package["filename"], "url": packageURL, "checksum": package["hash"]}})

				sublime.active_window().run_command("javatar", {"replaceMenu": {
					"name": "additional_packages",
					"menu": menu
				}})
				self.result = True
			else:
				getAction().addAction("javatar.util.updater", self.result_message)
				self.result = False

		except Exception as e:
			self.result_message = "Javatar packages update has failed: "+ str(e)
			getAction().addAction("javatar.util.updater", self.result_message)
			self.result = False
