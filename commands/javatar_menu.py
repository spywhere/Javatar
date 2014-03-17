import sublime_plugin
from ..QuickMenu import *
from ..utils.javatar_actions import *


class JavatarCommand(sublime_plugin.WindowCommand):
	qm = None
	menuStable = {
		"main": {
			"items": [["Builds...", "Build system"], ["Calls...", "Insert class informations"], ["Create...", "Create a new class"], ["Operations...", "Do a Java operations"]],
			"actions": [
				{
					"name": "builds"
				}, {
					"name": "calls"
				}, {
					"name": "creates"
				}, {
					"name": "operations"
				}
			]
		},
		"builds": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Project", "Build all classes in project"], ["Package", "Build all classes in current package"], ["Current Class", "Build current class"]],
			"actions": [
				{
					"name": "main"
				}, {
					"command": "javatar_build",
					"args": {
						"type": "project"
					}
				}, {
					"command": "javatar_build",
					"args": {
						"type": "package"
					}
				}, {
					"command": "javatar_build",
					"args": {
						"type": "class"
					}
				}
			]
		},
		"calls": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Package Name", "Return package path from root"], ["Subpackage Name", "Return current package name"], ["Full Class Name", "Return class path from root"], ["Class Name", "Return current class name"]],
			"actions": [
				{
					"name": "main"
				}, {
					"command": "javatar_call",
					"args": {
						"type": "package_name"
					}
				}, {
					"command": "javatar_call",
					"args": {
						"type": "subpackage_name"
					}
				}, {
					"command": "javatar_call",
					"args": {
						"type": "full_class_name"
					}
				}, {
					"command": "javatar_call",
					"args": {
						"type": "class_name"
					}
				}
			]
		},
		"creates": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"],["Package", "Create a new package"]],
			"actions": [
				{
					"name": "main"
				}, {
					"command": "javatar_create_package"
				}
			]
		},
		"operations": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Correct Class", "Correct package and class name in current file"]],
			"actions": [
				{
					"name": "main"
				}, {
					"command": "javatar_correct_class"
				}
			]
		},
		"dev": {
			"items": [["Back", "Back to previous menu"], ["Operations: Organize Imports", "Correct class imports in current file"], ["Operations: Rename Class", "Rename current class"], ["Operations: Rename Package", "Rename current package"], ["Prettify JSON", "Reformat current document as pretty JSON"], ["Generate SHA-256 Hash from URL", "Calculate checksum from url"], ["Generate SHA-256 Hash", "Calculate checksum for current document"], ["Convert Imports", "Convert Javatar Imports to Javatar Packages"], ["Testing", "For testing and experimenting new feature"]],
			"actions": [
				{
					"name": "main"
				}, {
					"command": "javatar_organize_imports"
				}, {
					"command": "javatar_rename_operation",
					"args": {
						"type": "class"
					}
				}, {
					"command": "javatar_rename_operation",
					"args": {
						"type": "package"
					}
				}, {
					"command": "javatar_util",
					"args": {
						"type": "tojson"
					}
				}, {
					"command": "javatar_util",
					"args": {
						"type": "remote_hash"
					}
				}, {
					"command": "javatar_util",
					"args": {
						"type": "hash"
					}
				}, {
					"command": "javatar_convert"
				}, {
					"command": "javatar_util",
					"args": {
						"type": "test"
					}
				}
			]
		},
		"help": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Download Packages", "Download additional Java packages..."], ["Actions History", "Generate a report on Javatar actions history"], ["Actions History (Custom)", "Generate a report on Javatar actions history using custom selector"]],
			"actions": [
				{
					"name": "main"
				}, {
					"name": "additional_packages"
				}, {
					"command": "javatar_help",
					"args": {
						"action": "actions_history",
						"selector": ""
					}
				}, {
					"command": "javatar_help",
					"args": {
						"action": "actions_history"
					}
				}
			]
		},
		"additional_packages": {
			"selected_index": 1,
			"items": [["Back", "Back to previous menu"], ["No package available", "Please check back later"]],
			"actions": [
				{
					"name": "help"
				}, {

				}
			]
		}
	}

	def run(self, menu=None, action=None, replaceMenu=None):
		if self.qm is None:
			from ..utils import getSnippetList, isStable, isDebug
			self.qm = QuickMenu(self.menuStable)
			# Create a menu for development channel
			if not isStable():
				self.qm.addItems("main", [["Development Section...", "All testing features"]], [{"name":"dev"}])

			# Generate action for Create menu
			actions = []
			for snippet in getSnippetList():
				actions += [{"command":"javatar_create","args":{"type":snippet[0]}}]
			self.qm.addItems("creates", getSnippetList(), actions)

			# Always add Help and Support at the end
			self.qm.addItems("main", [["Help and Support...", "Utilities for Help and Support on Javatar"]], [{"name":"help"}])

			# Quick reload menu
			if isDebug():
				self.qm.insertItem("main", 0, ["Reload Javatar", "Reload Javatar modules (debug only)"], {"command":"javatar_util", "args": {"type": "reload"}})
		if replaceMenu is not None:
			self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
			return
		self.qm.show(self.window, self.select, menu, action)

	def select(self, info):
		if info["index"] < 0:
			getAction().addAction("javatar.menu", "Exit menu [from_sublime="+str(info["from_sublime"])+"]")
		else:
			getAction().addAction("javatar.menu", "Select item "+ str(info["items"][info["index"]]) +" [from_sublime="+str(info["from_sublime"])+"]")
