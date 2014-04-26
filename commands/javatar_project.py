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
			if os.path.isfile(pathname) and is_java(pathname):
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
		source_folders = [[get_path("name", get_path("project_dir")), get_path("project_dir")+os.sep]]
		source_folders += self.get_source_folder(get_path("project_dir"))
		folders = []
		rootlen = len(get_path("project_dir"))
		for name, folder in source_folders:
			if self.is_source_folder(folder):
				folders.append([name, folder[rootlen:]])
		return folders

	def run(self, actiontype):
		get_action().add_action("javatar.command.project.run", "Project Settings [type="+actiontype+"]")
		self.actiontype = actiontype
		if actiontype == "set_source_folder":
			self.panel_list = self.get_folders()
			if len(self.panel_list) < 1:
				sublime.error_message("No source folder available")
				return
			sublime.active_window().show_quick_panel(self.panel_list, self.on_panel_complete)

	def on_panel_complete(self, index):
		if self.actiontype == "set_source_folder":
			source_rel_path = get_path("join", get_path("name", get_path("project_dir")), self.panel_list[index][1][1:])
			set_settings("source_folder", get_path("join", get_path("project_dir"), self.panel_list[index][1][1:]), True)
			sublime.set_timeout(lambda: show_status("Source folder \""+source_rel_path+"\" is set", None, False), 500)
