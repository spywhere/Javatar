import sublime
import sublime_plugin
import hashlib
import urllib.request
from ..utils import *

class JavatarUtilCommand(sublime_plugin.TextCommand):
	def run(self, edit, type="", text="", region=None, dest=None):
		if type == "insert":
			self.view.insert(edit, 0, text)
		elif type == "add":
			self.view.insert(edit, self.view.size(), text)
		elif type == "replace":
			self.view.insert(edit, region, text)
		elif type == "set_read_only":
			self.view.set_read_only(True)
		elif type == "test":
			if not isStable():
				self.view.show_popup_menu(["A", "B"], self.nothing)
		elif type == "remote_hash":
			if not isStable():
				sublime.active_window().show_input_panel("URL:", "", self.remote_hash, None, None)
		elif type == "hash":
			if not isStable():
				print(hashlib.sha256(self.view.substr(sublime.Region(0,self.view.size())).encode("utf-8")).hexdigest())
		elif type == "tojson":
			if not isStable():
				jsonObj = sublime.decode_value(self.view.substr(sublime.Region(0,self.view.size())))
				self.view.replace(edit, sublime.Region(0,self.view.size()), sublime.encode_value(jsonObj, True));
		elif type == "reload":
			if isDebug():
				getAction().addAction("javatar.command.utils.reload", "Reload Javatar")
				print("Reloading Javatar...")
				import sys
				from imp import reload
				for mod in sys.modules:
					if mod.lower().startswith("javatar") and not mod.lower().endswith("_utils") and sys.modules[mod] is not None:
						print("Reloading module " + mod + "...")
						reload(sys.modules[mod])
				from ..Javatar import plugin_loaded
				plugin_loaded()

	def remote_hash(self, url):
		try:
			urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()))
			data = urllib.request.urlopen(url).read()
			datahash = hashlib.sha256(data).hexdigest()
			print("Hash: " + datahash)
		except Exception:
			print("Error occurred while remote_hash")

	def nothing(self, index=-1):
		pass

	def description(self, type="", text="", dest=None):
		return dest

class JavatarReloadPackagesCommand(sublime_plugin.WindowCommand):
	def run(self):
		resetPackages()
		loadPackages()

class JavatarConvertCommand(sublime_plugin.WindowCommand):
	def run(self):
		for filepath in sublime.find_resources("*.javatar-imports"):
			packages_file = {"name":getPath("name", filepath), "packages":{}}
			imports_file = sublime.decode_value(sublime.load_resource(filepath))
			total_package = 0
			total_class = 0
			for imports in imports_file:
				if "package" in imports:
					total_package += 1
					package = imports["package"]
					packages_file["packages"][package] = {}
					if "default" in imports:
						packages_file["packages"][package]["default"] = imports["default"]
					if "interface" in imports:
						packages_file["packages"][package]["interface"] = []
						total_class += len(imports["interface"])
						for clss in imports["interface"]:
							packages_file["packages"][package]["interface"].append({"name":clss,"fields":[],"methods:":[]})
					if "class" in imports:
						packages_file["packages"][package]["class"] = []
						total_class += len(imports["class"])
						for clss in imports["class"]:
							packages_file["packages"][package]["class"].append({"name":clss,"fields":[],"methods:":[]})
					if "enum" in imports:
						packages_file["packages"][package]["enum"] = []
						total_class += len(imports["enum"])
						for clss in imports["enum"]:
							packages_file["packages"][package]["enum"].append({"name":clss,"fields":[],"methods:":[]})
					if "exception" in imports:
						packages_file["packages"][package]["exception"] = []
						total_class += len(imports["exception"])
						for clss in imports["exception"]:
							packages_file["packages"][package]["exception"].append({"name":clss,"fields":[],"methods:":[]})
					if "error" in imports:
						packages_file["packages"][package]["error"] = []
						total_class += len(imports["error"])
						for clss in imports["error"]:
							packages_file["packages"][package]["error"].append({"name":clss,"fields":[],"methods:":[]})
					if "annotation" in imports:
						packages_file["packages"][package]["annotation"] = []
						total_class += len(imports["annotation"])
						for clss in imports["annotation"]:
							packages_file["packages"][package]["annotation"].append({"name":clss,"fields":[],"methods:":[]})
					if "type" in imports:
						packages_file["packages"][package]["type"] = []
						total_class += len(imports["type"])
						for clss in imports["type"]:
							packages_file["packages"][package]["type"].append({"name":clss,"fields":[],"methods:":[]})
			with open(getPath("join", getPath("parent", sublime.packages_path()), filepath.replace(".javatar-imports", "-converted.javatar-packages")), "w") as filew:
				print(sublime.encode_value(packages_file, True), file=filew)
				sublime.message_dialog("Conversion Done\nTotal Packages: " + str(total_package) + "\nTotal Classes: " + str(total_class))