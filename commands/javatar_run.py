import sublime
import sublime_plugin
from ..utils import *

class JavatarRunMainCommand(sublime_plugin.WindowCommand):
	def run(self):
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
			self.on_build_done()
		else:
			sublime.error_message("Current file is not main class")

	def on_build_done(self):
		getAction().addAction("javatar.command.run.on_build_done", "Run main class")
		class_path = normalizePackage(getCurrentPackage()+"."+getClassName())
		self.class_name = getClassName()
		self.view = self.window.new_file()
		self.view.set_syntax_file("Packages/Javatar/syntax/JavaStackTrace.tmLanguage")
		self.view.set_name("Running " + self.class_name + " ...")
		self.view.set_scratch(True)
		shell = JavatarShell("java "+class_path, self.view, self.on_complete)
		shell.set_cwd(getPath("source_folder"))
		shell.start()
		ThreadProgress(shell, "Running Javatar Shell", "Javatar Shell has been stopped")

	def on_complete(self, elapse_time, return_code):
		if return_code is not None:
			self.view.set_name(self.class_name + " Ended (Return: " + str(return_code) + ") [{0:.2f}s]".format(elapse_time))