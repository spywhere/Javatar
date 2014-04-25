import sublime
import sublime_plugin
from ..utils import *

class JavatarRunMainCommand(sublime_plugin.WindowCommand):
	def run(self):
		if isFile():
			found_main = False
			view = sublime.active_window().active_view()
			method_regions = view.find_by_selector("entity.name.function.java")
			for region in method_regions:
				if view.substr(region) == "main":
					found_main = True
					break
			if found_main:
				file_path = view.file_name()[:-4]+"class"
				if not getPath("exist", file_path):
					sublime.error_message("File is not compiled")
					return
				self.on_run()
			else:
				sublime.error_message("Current file is not main class")
		else:
			sublime.error_message("Unknown class location")

	def on_run(self):
		getAction().addAction("javatar.command.run.on_run", "Run main class")
		class_path = normalizePackage(getCurrentPackage()+"."+getClassName())
		file_path = sublime.active_window().active_view().file_name()
		self.class_name = getClassName()
		self.view = self.window.new_file()
		self.view.set_syntax_file("Packages/Javatar/syntax/JavaStackTrace.tmLanguage")
		self.view.set_name("Running " + self.class_name + " ...")
		self.view.set_scratch(True)

		run_script = getSettings("run_command")
		run_script = run_script.replace("$file_path", getPath("parent", file_path))
		run_script = run_script.replace("$file_name", getPath("name", file_path))
		run_script = run_script.replace("$file", file_path)
		run_script = run_script.replace("$full_class_path", class_path)
		run_script = run_script.replace("$class_name", self.class_name)
		run_script = run_script.replace("$package", getCurrentPackage())
		run_script = run_script.replace("$packages_path", sublime.packages_path())
		if self.window.project_file_name() is not None:
			run_script = run_script.replace("$project_path", getPath("parent", self.window.project_file_name()))
			run_script = run_script.replace("$project_name", getPath("name", self.window.project_file_name()))
			run_script = run_script.replace("$project", self.window.project_file_name())

		shell = JavatarShell(run_script, self.view, self.on_complete)
		shell.set_cwd(getPath("source_folder"))
		shell.start()
		ThreadProgress(shell, "Running Javatar Shell", "Javatar Shell has been stopped")

	def on_complete(self, elapse_time, return_code):
		if return_code is not None:
			self.view.set_name(self.class_name + " Ended (Return: " + str(return_code) + ") [{0:.2f}s]".format(elapse_time))