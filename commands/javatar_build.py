import sublime
import sublime_plugin
from time import clock, sleep
from ..utils import *


class JavatarBuildCommand(sublime_plugin.WindowCommand):
	build_list = []
	build_size = -1
	source_folder = None
	view = None

	def build(self):
		self.start_time = clock()
		self.view = None
		self.source_folder = getPath("source_folder")
		self.build_size = len(self.build_list)
		self.progress = MultiThreadProgress("Preparing build", None, self.on_build_thread_complete, self.on_all_complete)
		num_thread = 1
		if getSettings("parallel_build") > num_thread:
			num_thread = getSettings("parallel_build")
		for i in range(num_thread):
			self.on_build_thread_complete(None)

	def on_build_thread_complete(self, thread):
		if self.build_size <= 0:
			return
		if self.build_size > 0 and self.view is not None and self.view.window() is None:
			self.build_size = -1
			return
		if len(self.build_list) > 0:
			file_path = self.build_list[0]
			del self.build_list[0]
			build = self.create_build(file_path)
			self.progress.add(build, getPath("name", file_path))
			if not self.progress.running:
				self.progress.run()
			if self.view is not None:
				self.view.set_name(self.progress.get_message())
		self.progress.set_message("[" + str(self.build_size-len(self.build_list)) + "/" + str(self.build_size) + "] Building ")

	def create_build(self, file_path):
		build_script = getSettings("build_command")
		build_script = build_script.replace("$file_path", getPath("parent", file_path))
		build_script = build_script.replace("$file_name", getPath("name", file_path))
		build_script = build_script.replace("$file", file_path)
		build_script = build_script.replace("$full_class_path", normalizePackage(getCurrentPackage()+"."+getClassName()))
		build_script = build_script.replace("$class_name", getClassName())
		build_script = build_script.replace("$package", getCurrentPackage())
		build_script = build_script.replace("$packages_path", sublime.packages_path())
		if self.window.project_file_name() is not None:
			build_script = build_script.replace("$project_path", getPath("parent", self.window.project_file_name()))
			build_script = build_script.replace("$project_name", getPath("name", self.window.project_file_name()))
			build_script = build_script.replace("$project", self.window.project_file_name())

		shell = JavatarSilentShell(build_script, self.on_build_done)
		shell.set_cwd(self.source_folder)
		shell.start()
		return shell

	def on_build_done(self, elapse_time, data, return_code):
		if self.build_size > 0 and self.view is not None and self.view.window() is None:
			self.build_size = -1
			return
		if data is not None:
			if self.view is None:
				self.view = self.window.new_file()
				self.view.set_name("Preparing build log...")
				self.view.set_syntax_file("Packages/Javatar/syntax/JavaCompilationError.tmLanguage")
				# Prevent view access while creating which cause double view to create
				sleep(getSettings("build_log_delay"))
			self.view.set_scratch(True)
			self.view.run_command("javatar_util", {"util_type": "add", "text": data})

	def on_all_complete(self):
		if self.build_size < 0:
			sublime.status_message("Building Cancelled")
			getAction().addAction("javatar.command.build.complete", "Building Cancelled")
			return

		self.build_size = -1
		if self.view is not None:
			self.view.set_name("Building Finished [{0:.2f}s]".format(clock()-self.start_time))
		sublime.status_message("Building Finished [{0:.2f}s]".format(clock()-self.start_time))
		getAction().addAction("javatar.command.build.complete", "Building Finished")

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
					getAction().addAction("javatar.command.build.build_working", "Build working files")
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
