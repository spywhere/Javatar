import re
import sublime
import threading
from .javatar_actions import *
from .javatar_thread import *
from ..utils.javatar_utils import toReadableSize


INSTALLED_PACKAGES = []
SNIPPETS = []
DEFAULT_PACKAGES = []

'''
Allow to include a javatar-packages files into project (atleast easier for bukkit autocomplete)
Allow a new javatar format for packaging a custom jar file (atleast easier for bukkit plugin jar file)
'''

def resetSnippetsAndPackages():
	getAction().addAction("javatar.util.collection.reset", "Reset all snippets")
	global SNIPPETS
	SNIPPETS = []
	resetPackages()


def resetPackages():
	getAction().addAction("javatar.util.collection.reset", "Reset all default packages")
	global INSTALLED_PACKAGES, DEFAULT_PACKAGES
	INSTALLED_PACKAGES = []
	DEFAULT_PACKAGES = []


def getInstalledPackages():
	return INSTALLED_PACKAGES


def getInstalledPackage(name):
	for package in INSTALLED_PACKAGES:
		if package["name"].startswith(name):
			return package
	return None


def loadSnippetsAndPackages():
	getAction().addAction("javatar.util.collection.get_snippet_files", "Load snippets")
	thread = JavatarSnippetsLoaderThread(snippetsComplete)
	thread.start()
	ThreadProgress(thread, "Loading Javatar snippets", "Javatar snippets has been loaded")


def snippetsComplete(data):
	global SNIPPETS
	SNIPPETS = data
	loadPackages()


def loadPackages(no_require=False):
	getAction().addAction("javatar.util.collection.get_package_files", "Load Java default packages")
	thread = JavatarPackagesLoaderThread(packagesComplete, no_require)
	thread.start()
	ThreadProgress(thread, "Loading Javatar packages", "Javatar packages has been loaded")


def packagesComplete(data, no_require=False):
	global INSTALLED_PACKAGES, DEFAULT_PACKAGES
	INSTALLED_PACKAGES = data["installed_packages"]
	DEFAULT_PACKAGES = data["default_packages"]

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
	for package in getInstalledPackages():
		install_update = True
		installed_menu["actions"].append({"command": "javatar_install", "args": {"installtype": "uninstall_package", "name": package["name"], "filename": package["path"]}})
		installed_menu["items"].append([package["name"], "Installed (" + toReadableSize(package["path"]) + ")."])
	if install_update:
		installed_menu["selected_index"] = 2
		sublime.active_window().run_command("javatar", {"replaceMenu": {
		"name": "uninstall_packages",
		"menu": installed_menu
		}})

	from .javatar_updater import updatePackages
	updatePackages(no_require)


def getPackages():
	packages = []
	for pck in DEFAULT_PACKAGES:
		packages.append(pck)
	return packages


def getSnippet(name):
	for snippet in SNIPPETS:
		if snippet["class"] == name:
			return snippet["data"]
	return None


def getSnippetName(index):
	return SNIPPETS[index]["class"]


def getSnippetList():
	slist = []
	for snippet in SNIPPETS:
		slist.append([snippet["class"], snippet["description"]])
	return slist


class JavatarSnippetsLoaderThread(threading.Thread):
	def __init__(self, on_complete=None):
		self.on_complete = on_complete
		threading.Thread.__init__(self)

	def analyseSnippet(self, file):
		getAction().addAction("javatar.util.collection.analyse_snippet", "Analyse snippet [file="+file+"]")
		data = sublime.load_resource(file)
		classScope = None
		classRe = re.search("%class:(.*)%(\\s*)", data, re.M)
		if classRe is not None:
			classScope = classRe.group(0)
			data = re.sub("%class:(.*)%(\\s*)", "", data)
			classScope = re.sub("(\\s*)$", "", classScope)
			classScope = classScope[7:-1]

		if classScope is None or classScope == "":
			from .javatar_utils import getPath
			classScope = getPath("name", file)[:-8]

		descriptionScope = ""
		descriptionRe = re.search("%description:(.*)%(\\s*)", data, re.M)
		if descriptionRe is not None:
			descriptionScope = descriptionRe.group(0)
			data = re.sub("%description:(.*)%(\\s*)", "", data)
			descriptionScope = re.sub("(\\s*)$", "", descriptionScope)
			descriptionScope = descriptionScope[13:-1]
		return {"file": file, "class": classScope, "description": descriptionScope, "data": data}

	def run(self):
		snippets = []

		from .javatar_utils import getPath
		for filepath in sublime.find_resources("*.javatar"):
			filename = getPath("name", filepath)
			getAction().addAction("javatar.util.collection", "Javatar snippet " + filename + " loaded")
			print("Javatar snippet " + filename + " loaded")
			snippets.append(self.analyseSnippet(filepath))

		self.result = True
		if self.on_complete is not None:
			sublime.set_timeout(lambda: self.on_complete(snippets), 10)


class JavatarPackagesLoaderThread(threading.Thread):
	def __init__(self, on_complete=None, no_require=False):
		self.installed_packages = []
		self.on_complete = on_complete
		self.no_require = no_require
		threading.Thread.__init__(self)

	def countClasses(self, imports):
		packages = 0
		classes = 0
		if "packages" in imports:
			for packageName in imports["packages"]:
				package = imports["packages"][packageName]
				packages += 1
				if "interface" in package:
					classes += len(package["interface"])
				if "class" in package:
					classes += len(package["class"])
				if "enum" in package:
					classes += len(package["enum"])
				if "exception" in package:
					classes += len(package["exception"])
				if "error" in package:
					classes += len(package["error"])
				if "annotation" in package:
					classes += len(package["annotation"])
				if "type" in package:
					classes += len(package["type"])
		return [packages, classes]

	def analysePackage(self, filepath):
		getAction().addAction("javatar.util.collection.analyse_import", "Analyse package [file="+filepath+"]")
		try:
			from .javatar_utils import getPath
			imports = sublime.decode_value(sublime.load_resource(filepath))
			if "experiment" in imports and imports["experiment"]:
				return None
			filename = getPath("name", filepath)
			if "name" in imports:
				filename = imports["name"]
			count = self.countClasses(imports)
			self.installed_packages.append({"name": filename, "path": filepath})
			print("Javatar package \"" + filename + "\" loaded with " + str(count[1]) + " classes in " + str(count[0]) + " packages")
			return imports
		except ValueError:
			sublime.error_message("Invalid JSON format")
		return None

	def run(self):
		default_packages = []
		from .javatar_utils import getPath
		for filepath in sublime.find_resources("*.javatar-packages"):
			filename = getPath("name", filepath)
			getAction().addAction("javatar.util.collection", "Javatar default package " + filename + " loaded")
			imports = self.analysePackage(filepath)
			if imports is not None:
				default_packages.append(imports)

		data = {
			"installed_packages": self.installed_packages,
			"default_packages": default_packages
		}
		self.result = True
		if self.on_complete is not None:
			sublime.set_timeout(lambda: self.on_complete(data, self.no_require), 10)
