import os
import sublime
import sublime_plugin
from ..utils import *


def getInfo(text):
	relative = True
	if text.startswith("~"):
		text = text[1:]
		relative = False

	if not isProject() and not isFile():
		sublime.error_message("Unknown package location")
		return
	if not isPackage(text):
		sublime.error_message("Invalid package naming")
		return

	package = normalizePackage(getCurrentPackage(not relative) + "." + getPackagePath(text))
	className = getClassName(text)

	target_dir = makePackage(getPackageRootDir(), packageAsDirectory(package), True)
	target_dir = normalizePath(target_dir)
	package = toPackage(target_dir)
	file = getPath("join", getPackageRootDir(), getPath("join", packageAsDirectory(package), className + ".java"))
	return {"file": file, "package": package, "class": className, "relative": relative}


def getFileContents(classType, info):
	data = getSnippet(classType)
	if data is None:
		sublime.error_message("Snippet \"" + classType + "\" is not found")
		return None
	if info["package"] != "":
		data = data.replace("%package%", "package " + info["package"] + ";")
	else:
		data = data.replace("%package%", "")

	data = data.replace("%class%", info["class"])
	data = data.replace("%file%", info["file"])
	data = data.replace("%file_name%", getPath("name", info["file"]))
	data = data.replace("%package_path%", getCurrentPackage())
	return data


def insertAndSave(view, contents):
	view.run_command("insert_snippet", {"contents": contents})
	view.run_command("save")


def createClassFile(file, contents, msg):
	if contents is None:
		return
	if os.path.exists(file):
		sublime.error_message(msg)
		return
	open(file, "w")
	view = sublime.active_window().open_file(file)
	view.set_syntax_file("Packages/Java/Java.tmLanguage")
	sublime.set_timeout(lambda: insertAndSave(view, contents), 100)


class JavatarCreateCommand(sublime_plugin.WindowCommand):
	def run(self, text="", create_type=""):
		getAction().addAction("javatar.command.create.run", "Create [create_type=" + create_type + "]")
		if create_type != "":
			self.showInput(-1, create_type)
			return
		if text != "":
			info = getInfo(text)
			getAction().addAction("javatar.command.create.run", "Create [info=" + str(info) + "]")
			createClassFile(info["file"], getFileContents(self.create_type, info), self.create_type + "\"" + info["class"] + "\" already exists")
			sublime.set_timeout(lambda: showStatus(self.create_type + " \"" + info["class"] + "\" is created within package \"" + toReadablePackage(info["package"], True) + "\""), 500)

	def showInput(self, index, create_type=""):
		if create_type != "" or index >= 0:
			if create_type != "":
				self.create_type = create_type
			else:
				self.create_type = getSnippetName(index)
			sublime.active_window().show_input_panel(self.create_type + " Name:", "", self.run, "", "")
