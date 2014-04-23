import sublime
import sublime_plugin
import os
import pty
import select
from subprocess import Popen, STDOUT
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
			master, slave = pty.openpty()
			file_path = view.file_name()[:-4]+"class"
			if not getPath("exist", file_path):
				sublime.error_message("File is not compiled")
				return
			self.on_build_done()
		else:
			sublime.error_message("Current file is not main class")

	def on_build_done(self):
		view = sublime.active_window().active_view()
		self.class_path = toPackage(view.file_name(), True).split(".")
		del self.class_path[-1]
		self.class_path = ".".join(self.class_path)
		self.view = self.window.new_file()
		self.view.set_syntax_file("Packages/Javatar/syntax/JavaStackTrace.tmLanguage")
		self.view.set_name("Running " + self.class_path + " ...")
		self.view.set_scratch(True)
		shell = JavatarShell(["java", self.class_path], self.view, self.on_complete)
		shell.set_cwd(getPath("source_folder"))
		shell.start()
		ThreadProgress(shell, "Running Javatar Shell", "Javatar Shell has been stopped")

	def on_complete(self, elapse_time, proper):
		if proper:
			self.view.set_name(self.class_path + " Ended [{0:.2f}s]".format(elapse_time))