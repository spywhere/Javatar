import sublime
import sublime_plugin
from time import clock, sleep
from ..utils import *


# Create .jar using "jar" command
# http://docs.oracle.com/javase/7/docs/technotes/tools/windows/jar.html


class JavatarBuildCommand(sublime_plugin.WindowCommand):
	build_list = []
	build_size = -1
	view = None

	def build(self):
		self.start_time = clock()
		self.view = None
		self.build_size = len(self.build_list)
		self.progress = MultiThreadProgress("Preparing build", None, self.on_build_thread_complete, self.on_all_complete)
		num_thread = 1
		if get_settings("parallel_build") > num_thread:
			num_thread = get_settings("parallel_build")
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
			self.progress.add(build, get_path("name", file_path))
			if not self.progress.running:
				self.progress.run()
			if self.view is not None:
				self.view.set_name(self.progress.get_message())
		self.progress.set_message("[" + str(self.build_size-len(self.build_list)) + "/" + str(self.build_size) + "] Building ")

	def create_build(self, file_path):
		self.macro_data["sourcepath"] = "-sourcepath \"" + get_path("source_folder") + "\""
		dependencies = get_dependencies()
		dependencies_param = None
		for dependency in dependencies:
			from os import pathsep
			if dependencies_param is None:
				dependencies_param = "-classpath ."+pathsep+"\""+dependency[0]+"\""
			else:
				dependencies_param += pathsep+"\""+dependency[0]+"\""
		self.macro_data["classpath"] = dependencies_param
		self.macro_data["d"] = ""
		if get_settings("build_output_location") != "":
			output_dir = parse_macro(get_settings("build_output_location"), self.macro_data, file_path)
			from os import makedirs
			from os.path import isdir
			if not isdir(output_dir):
				makedirs(output_dir)
			self.macro_data["d"] = "-d \"" + output_dir + "\""
		build_script = parse_macro(get_settings("build_command"), self.macro_data, file_path)
		shell = JavatarSilentShell(build_script, self.on_build_done)
		shell.set_cwd(parse_macro(get_settings("build_location"), self.macro_data))
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
				sleep(get_settings("build_log_delay"))
			self.view.set_scratch(True)
			self.view.run_command("javatar_util", {"util_type": "add", "text": data})

	def on_all_complete(self):
		if self.build_size < 0:
			sublime.status_message("Building Cancelled")
			get_action().add_action("javatar.command.build.complete", "Building Cancelled")
			return

		self.build_size = -1
		if self.view is not None:
			self.view.set_name("Building Finished [{0:.2f}s]".format(clock()-self.start_time))
		sublime.status_message("Building Finished [{0:.2f}s]".format(clock()-self.start_time))
		get_action().add_action("javatar.command.build.complete", "Building Finished")

	def buildAll(self, dir_path):
		for path, subdirs, files in os.walk(dir_path):
			for filename in files:
				if is_java(get_path("join", path, filename)):
					self.build_list.append(get_path("join", path, filename))
		if len(self.build_list) > 0:
			get_action().add_action("javatar.command.build.build_all", "Build all")
			self.build()
			return True
		else:
			return False

	def run(self, build_type=""):
		self.macro_data = get_macro_data()
		self.build_list = []
		get_action().add_action("javatar.command.build.run", "Build [build_type=" + build_type + "]")
		view = sublime.active_window().active_view()
		if build_type == "project":
			if is_project() or is_file():
				for view in self.window.views():
					if is_java(view.file_name()):
						if view.is_dirty():
							if get_settings("automatic_save"):
								self.window.run_command("save_all")
							else:
								sublime.error_message("Some Java files are not saved")
								return
				if not self.buildAll(get_package_root_dir()):
					sublime.error_message("No class to build")
			else:
				sublime.error_message("Unknown package location")
		elif build_type == "package":
			if is_file():
				for view in self.window.views():
					if is_java(view.file_name()):
						if view.is_dirty():
							if get_settings("automatic_save"):
								self.window.run_command("save_all")
							else:
								sublime.error_message("Some Java files are not saved")
								return
				if not self.buildAll(get_path("current_dir")):
					sublime.error_message("No class to build")
			else:
				sublime.error_message("Unknown package location")
		elif build_type == "working":
			if is_file():
				for view in self.window.views():
					if is_java(view.file_name()):
						self.build_list.append(view.file_name())
						if view.is_dirty():
							if get_settings("automatic_save"):
								self.window.run_command("save_all")
							else:
								sublime.error_message("Some Java files are not saved")
								return
				if len(self.build_list) > 0:
					get_action().add_action("javatar.command.build.build_working", "Build working files")
					self.build()
				else:
					sublime.error_message("No class to build")
			else:
				sublime.error_message("Unknown package location")
		elif build_type == "class":
			if is_file():
				if is_java(view.file_name()):
					if self.window.active_view().is_dirty():
						if get_settings("automatic_save"):
							self.window.run_command("save")
						else:
							sublime.error_message("Current file is not saved")
							return
					get_action().add_action("javatar.command.build.build_file", "Build file")
					self.build_list.append(view.file_name())
					self.build()
				else:
					sublime.error_message("Current file is not Java")
			else:
				sublime.error_message("Unknown class location")
