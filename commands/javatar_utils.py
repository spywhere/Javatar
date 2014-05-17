import sublime
import sublime_plugin
import hashlib
import urllib.request
from ..parser import *
from ..utils import *


class JavatarUtilCommand(sublime_plugin.TextCommand):
	def run(self, edit, util_type="", text="", region=None, dest=None):
		if util_type == "insert":
			self.view.insert(edit, 0, text)
		elif util_type == "add":
			self.view.insert(edit, self.view.size(), text)
		elif util_type == "replace":
			self.view.insert(edit, region, text)
		elif util_type == "clear":
			self.view.erase(edit, sublime.Region(0, self.view.size()))
		elif util_type == "set_read_only":
			self.view.set_read_only(True)
		elif util_type == "clear_read_only":
			self.view.set_read_only(False)
		elif util_type == "test":
			if not is_stable():
				self.view.show_popup_menu(["A", "B"], self.nothing)
		elif util_type == "remote_hash":
			if not is_stable():
				sublime.active_window().show_input_panel("URL:", "", self.remote_hash, None, None)
		elif util_type == "hash":
			if not is_stable():
				print(hashlib.sha256(self.view.substr(sublime.Region(0, self.view.size())).encode("utf-8")).hexdigest())
		elif util_type == "tojson":
			if not is_stable():
				jsonObj = sublime.decode_value(self.view.substr(sublime.Region(0, self.view.size())))
				self.view.replace(edit, sublime.Region(0, self.view.size()), sublime.encode_value(jsonObj, True));
		elif util_type == "parse":
			try:
				grammars = sublime.find_resources("Java8.javatar-grammar")
				if len(grammars) > 0:
					scope = GrammarParser(sublime.decode_value(sublime.load_resource(grammars[0])))
					parse_output = scope.parse_grammar(self.view.substr(sublime.Region(0, self.view.size())))
					status_text = ""
					if parse_output["success"]:
						if not is_stable():
							if text == "":
								nodes = scope.find_all()
							elif text == "#":
								selections = self.view.sel()
								nodes = scope.find_by_region([0, 0])
								if len(selections) > 0:
									first_sel = selections[0]
									if first_sel.empty():
										nodes = scope.find_by_region([first_sel.begin(), first_sel.end()])
									else:
										nodes = scope.find_inside_region([first_sel.begin(), first_sel.end()])
							else:
								nodes = scope.find_by_selectors(text)
							if text != "#":
								status_text = "Parsing got " + str(len(nodes)) + " tokens"
							for node in nodes:
								if text == "#":
									if status_text == "":
										status_text += node["name"]
									else:
										status_text += " " + node["name"]
								else:
									print("#" + str(node["begin"]) + ":" + str(node["end"]) + " => " + node["name"])
									print("   => " + node["value"])
							print("Total: " + str(len(nodes)) + " tokens")
					if not is_stable():
						if text != "#":
							if status_text != "" and str(parse_output["end"]) == str(self.view.size()):
								status_text += " in {elapse_time:.2f}s".format(elapse_time=scope.get_elapse_time())
							else:
								status_text = "Parsing failed [" + str(parse_output["end"]) + "/" + str(self.view.size()) + "] in {elapse_time:.2f}s".format(elapse_time=scope.get_elapse_time())
						print("Ending: " + str(parse_output["end"]) + "/" + str(self.view.size()))
						print("Parsing Time: {elapse_time:.2f}s".format(elapse_time=scope.get_elapse_time()))
						show_status(status_text, None, False)
			except Exception:
				print("Error occurred while parsing")
		elif util_type == "reload":
			if is_debug():
				get_action().add_action("javatar.command.utils.reload.run", "Reload Javatar")
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

	def description(self, util_type="", text="", dest=None):
		return dest

class JavatarReload_packagesCommand(sublime_plugin.WindowCommand):
	def run(self):
		get_action().add_action("javatar.command.utils.reload_packages.run", "Reload Packages")
		reset_packages()
		load_packages()

class JavatarConvertCommand(sublime_plugin.WindowCommand):
	def run(self):
		for filepath in sublime.find_resources("*.javatar-imports"):
			get_action().add_action("javatar.command.utils.convert.run", "Converting imports \""+get_path("name", filepath)+"\"")
			packages_file = {"name":get_path("name", filepath), "packages":{}}
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
			with open(get_path("join", get_path("parent", sublime.packages_path()), filepath.replace(".javatar-imports", "-converted.javatar-packages")), "w") as filew:
				print(sublime.encode_value(packages_file, True), file=filew)
				sublime.message_dialog("Conversion Done\nTotal Packages: " + str(total_package) + "\nTotal Classes: " + str(total_class))