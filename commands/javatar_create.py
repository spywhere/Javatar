import os
import sublime
import sublime_plugin
from ..utils import *


def getInfo(text):
	relative = True
	if text.startswith("~"):
		text = text[1:]
		relative = False

	if not is_project() and not is_file():
		sublime.error_message("Unknown package location")
		return
	if not is_package(text):
		sublime.error_message("Invalid package naming")
		return

	package = normalize_package(get_current_package(not relative) + "." + get_package_path(text))
	className = get_class_name_by_regex(text)

	target_dir = make_package(get_package_root_dir(), package_as_directory(package), True)
	target_dir = normalize_path(target_dir)
	package = to_package(target_dir)
	file_path = get_path("join", get_package_root_dir(), get_path("join", package_as_directory(package), className + ".java"))
	return {"file": file_path, "package": package, "class": className, "relative": relative}


def getFileContents(classType, info):
	data = get_snippet(classType)
	if data is None:
		sublime.error_message("Snippet \"" + classType + "\" is not found")
		return None
	if info["package"] != "":
		data = data.replace("%package%", "package " + info["package"] + ";")
	else:
		data = data.replace("%package%", "")

	data = data.replace("%class%", info["class"])
	data = data.replace("%file%", info["file"])
	data = data.replace("%file_name%", get_path("name", info["file"]))
	data = data.replace("%package_path%", get_current_package())
	return data


def insertAndSave(view, contents):
	view.run_command("insert_snippet", {"contents": contents})
	view.run_command("save")


def createClassFile(file_path, contents, msg):
	if contents is None:
		return
	if os.path.exists(file_path):
		sublime.error_message(msg)
		return
	open(file_path, "w")
	view = sublime.active_window().open_file(file_path)
	view.set_syntax_file("Packages/Java/Java.tmLanguage")
	sublime.set_timeout(lambda: insertAndSave(view, contents), 100)


class JavatarCreateCommand(sublime_plugin.WindowCommand):
	def run(self, text="", create_type=""):
		get_action().add_action("javatar.command.create.run", "Create [create_type=" + create_type + "]")
		if create_type != "":
			self.showInput(-1, create_type)
			return
		if text != "":
			info = getInfo(text)
			get_action().add_action("javatar.command.create.run", "Create [info=" + str(info) + "]")
			createClassFile(info["file"], getFileContents(self.create_type, info), self.create_type + "\"" + info["class"] + "\" already exists")
			sublime.set_timeout(lambda: show_status(self.create_type + " \"" + info["class"] + "\" is created within package \"" + to_readable_package(info["package"], True) + "\""), 500)

	def showInput(self, index, create_type=""):
		if create_type != "" or index >= 0:
			if create_type != "":
				self.create_type = create_type
			else:
				self.create_type = get_snippet_name(index)
			sublime.active_window().show_input_panel(self.create_type + " Name:", "", self.run, "", "")
