import sublime
import sublime_plugin
from ..utils import *


class JavatarProjectCommand(sublime_plugin.WindowCommand):
	def is_source_folder(self, path, can_empty=True):
		for name in os.listdir(path):
			pathname = os.path.join(path,name)
			if can_empty:
				if os.path.isdir(pathname):
					if self.is_source_folder(pathname):
						return True
			if os.path.isfile(pathname) and isJava(pathname):
				return True
		return False

	def get_source_folder(self, path):
		folder_list=[]
		for name in os.listdir(path):
			pathname = os.path.join(path,name)
			if os.path.isdir(pathname) and not name.startswith("."):
				folder_list.append([name, pathname])
				folder_list += self.get_source_folder(pathname)
		return folder_list

	def get_folders(self):
		source_folders = [[getPath("name", getPath("project_dir")), getPath("project_dir")+"/"]]
		source_folders += self.get_source_folder(getPath("project_dir"))
		folders = []
		rootlen = len(getPath("project_dir"))
		for name, folder in source_folders:
			if self.is_source_folder(folder):
				folders.append([name, folder[rootlen:]])
		return folders

	def run(self, actiontype):
		self.actiontype = actiontype
		if actiontype == "set_source_folder":
			self.panel_list = self.get_folders()
			if len(self.panel_list) < 1:
				sublime.error_message("No source folder available")
				return
			sublime.active_window().show_quick_panel(self.panel_list, self.on_panel_complete)

	def on_panel_complete(self, index):
		if self.actiontype == "set_source_folder":
			source_rel_path = getPath("join", getPath("name", getPath("project_dir")), self.panel_list[index][1][1:])
			setSettings("source_folder", getPath("join", getPath("project_dir"), self.panel_list[index][1][1:]), True)
			sublime.set_timeout(lambda: showStatus("Source folder \""+source_rel_path+"\" is set", None, False), 500)


class JavatarCreatePackageCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.showInput()

	def showInput(self):
		sublime.active_window().show_input_panel("Package Name:", "", self.createPackage, "", "")

	def createPackage(self, text):
		getAction().addAction("javatar.command.package.create_package", "Create package [package="+text+"]")
		relative = True
		if text.startswith("~"):
			text = text[1:]
			relative = False

		if not isProject() and not isFile():
			sublime.error_message("Cannot specify package location")
			return
		if not isPackage(text):
			sublime.error_message("Invalid package naming")
			return

		target_dir = makePackage(getPackageRootDir(relative), text)
		showStatus("Package \""+toPackage(target_dir)+"\" is created", None, False)
