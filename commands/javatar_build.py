import sublime
import sublime_plugin
from ..utils import *


class JavatarBuildCommand(sublime_plugin.WindowCommand):
	build_list = []
	build_size = -1
	view = None

	def build(self):
		if self.build_size > 0 and self.view is not None and self.view.window() is None:
			self.build_size = -1
			sublime.status_message("Building Cancelled")
			return
		if self.build_size < 0:
			self.view = None
			self.build_size = len(self.build_list)
		if len(self.build_list) > 0:
			file_path = self.build_list[0]
			del self.build_list[0]
			if self.view is not None:
				self.view.set_name("Building " + getPath("name", file_path))
			self.run_build(file_path)
		else:
			self.build_size = -1
			if self.view is not None:
				self.view.set_name("Building Finished")
				sublime.status_message("Building Finished")

	def run_build(self, file_path):
		build_script = []
		for cmd in getSettings("build_command"):
			script = cmd
			script = script.replace("$file_path", getPath("parent", file_path))
			script = script.replace("$file_name", getPath("name", file_path))
			script = script.replace("$file", file_path)
			script = script.replace("$packages", sublime.packages_path())
			if self.window.project_file_name() is not None:
				script = script.replace("$project_path", getPath("parent", self.window.project_file_name()))
				script = script.replace("$project_name", getPath("name", self.window.project_file_name()))
				script = script.replace("$project", self.window.project_file_name())
			build_script.append(script)

		shell = JavatarSilentShell(build_script, self.on_build_complete)
		shell.set_cwd(getPath("source_folder"))
		shell.start()
		ThreadProgress(shell, "[" + str(self.build_size-len(self.build_list)) + "/" + str(self.build_size) + "] Building " + getPath("name", file_path))

	def on_build_complete(self, elapse_time, data):
		if data is not None:
			if self.view is None:
				self.view = self.window.new_file()
				self.view.set_syntax_file("Packages/Javatar/syntax/JavaCompilationError.tmLanguage")
			self.view.set_scratch(True)
			self.view.run_command("javatar_util", {"util_type": "add", "text": data})
		self.build()

	def buildAll(self, dir_path):
		for path, subdirs, files in os.walk(dir_path):
			for filename in files:
				if isJava(getPath("join", path, filename)):
					self.build_list.append(getPath("join", path, filename))
		if len(self.build_list) > 0:
			getAction().addAction("javatar.command.build.build_all", "Build all")
			self.build()
			return True
		else:
			return False

	def run(self, build_type=""):
		self.build_list = []
		getAction().addAction("javatar.command.build.run", "Build [build_type=" + build_type + "]")
		view = sublime.active_window().active_view()
		if build_type == "project":
			if isProject() or isFile():
				for view in self.window.views():
					if isJava(view.file_name()):
						if view.is_dirty():
							if getSettings("automatic_save"):
								self.window.run_command("save_all")
							else:
								sublime.error_message("Some Java files are not saved")
								return
				if not self.buildAll(getPackageRootDir()):
					sublime.error_message("No class to build")
			else:
				sublime.error_message("Unknown package location")
		elif build_type == "package":
			if isFile():
				for view in self.window.views():
					if isJava(view.file_name()):
						if view.is_dirty():
							if getSettings("automatic_save"):
								self.window.run_command("save_all")
							else:
								sublime.error_message("Some Java files are not saved")
								return
				if not self.buildAll(getPath("current_dir")):
					sublime.error_message("No class to build")
			else:
				sublime.error_message("Unknown package location")
		elif build_type == "working":
			if isFile():
				for view in self.window.views():
					if isJava(view.file_name()):
						self.build_list.append(view.file_name())
						if view.is_dirty():
							if getSettings("automatic_save"):
								self.window.run_command("save_all")
							else:
								sublime.error_message("Some Java files are not saved")
								return
				if len(self.build_list) > 0:
					self.build()
				else:
					sublime.error_message("No class to build")
			else:
				sublime.error_message("Unknown package location")
		elif build_type == "class":
			if isFile():
				if isJava(view.file_name()):
					if self.window.active_view().is_dirty():
						if getSettings("automatic_save"):
							self.window.run_command("save")
						else:
							sublime.error_message("Current file is not saved")
							return
					getAction().addAction("javatar.command.build.build_file", "Build file")
					self.build_list.append(view.file_name())
					self.build()
				else:
					sublime.error_message("Current file is not Java")
			else:
				sublime.error_message("Unknown class location")
