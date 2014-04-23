import sublime_plugin
from ..utils import *


class JavatarCallCommand(sublime_plugin.TextCommand):
	def run(self, edit, call_type=""):
		getAction().addAction("javatar.command.call.run", "Call [call_type=" + call_type + "]")
		if not isJava():
			sublime.error_message("Current file is not Java")
			return
		sels = self.view.sel()
		for sel in sels:
			if call_type == "package_name":
				self.view.insert(edit, sel.a, getCurrentPackage())
			elif call_type == "subpackage_name":
				self.view.insert(edit, sel.a, getCurrentPackage().split(".")[-1])
			elif call_type == "full_class_name":
				self.view.insert(edit, sel.a, normalizePackage(getCurrentPackage()+"."+getClassName()))
			elif call_type == "class_name":
				self.view.insert(edit, sel.a, getClassName())

	def description(self, call_type=""):
		if call_type == "package_name":
			return "Insert Package Name"
		elif call_type == "subpackage_name":
			return "Insert Subpackage Name"
		elif call_type == "full_class_name":
			return "Insert Full Class Name"
		elif call_type == "class_name":
			return "Insert Class Name"
		return None
