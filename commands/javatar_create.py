import os
import sublime
import sublime_plugin
from ..utils import *


def get_info(text):
	relative = True
	if text.startswith("~"):
		text = text[1:]
		relative = False

	if not is_project() and not (is_project() and is_file()):
		sublime.error_message("Cannot specify package location")
		return
	if not is_package(text, True):
		sublime.error_message("Invalid package naming")
		return
	if relative and get_path("current_dir") is not None:
		create_directory = get_path("join", get_path("current_dir"), package_as_directory(get_package_path(text)))
	else:
		create_directory = get_path("join", get_package_root_dir(), package_as_directory(get_package_path(text)))

	visibilityMap = {
		"public": "public ",
		"default": "",
		"private": "private ",
		"protected": "protected "
	}
	modifierMap = {
		"abstract": "abstract ",
		"final": "final "
	}

	body = "${1}"
	visibility = visibilityMap["public"]
	modifier = ""
	extends = []
	implements = []
	package = to_package(get_path("relative", create_directory, get_package_root_dir()), False)
	make_package(create_directory, True)
	className = get_class_name_by_regex(text)

	for visibilityKeyword, visibilityCode in visibilityMap.items():
		if className.lower().startswith(visibilityKeyword):
			className = className[len(visibilityKeyword):]
			visibility = visibilityCode;
			break

	for modifierKeyword, modifierCode in modifierMap.items():
		if className.lower().startswith(modifierKeyword):
			className = className[len(modifierKeyword):]
			modifier = modifierCode
			break

	extendsComponent = className.split(":")
	if len(extendsComponent) > 1:
		className = extendsComponent[0]
		implementsComponent = extendsComponent[1].split("<")
		if len(implementsComponent) > 1:
			extends = implementsComponent[0].split(",")
			implements = implementsComponent[1].split(",")
		elif len(implementsComponent) > 0:
			extends = extendsComponent[1].split(",")

	implementsComponent = className.split("<")
	if len(implementsComponent) > 1:
		className = implementsComponent[0]
		extendsComponent = implementsComponent[1].split(":")
		if len(extendsComponent) > 1:
			implements = extendsComponent[0].split(",")
			extends = extendsComponent[1].split(",")
		elif len(extendsComponent) > 0:
			implements = implementsComponent[1].split(",")

	if className.lower().endswith("asmain"):
		className = className[:-6]
		body = "public static void main(String[] args) {\n\t\t${1}\n\t}"

	file_path = get_path("join", create_directory, className + ".java")
	return {"file": file_path, "package": package, "visibility": visibility, "modifier": modifier, "class": className, "extends": extends, "implements": implements, "body": body}


def get_file_contents(classType, info):
	data = get_snippet(classType)
	if data is None:
		sublime.error_message("Snippet \"" + classType + "\" is not found")
		return None
	if info["package"] != "":
		data = data.replace("%package%", "package " + info["package"] + ";")
	else:
		data = data.replace("%package%", "")

	inheritance = ""
	# Enum can only implements interfaces
	# Interface can only extends another interface
	if classType != "Enumeration" and len(info["extends"]) > 0:
		inheritance = " extends " + ", ".join(info["extends"])
	if classType != "Interface" and len(info["implements"]) > 0:
		inheritance += " implements " + ", ".join(info["implements"])

	data = data.replace("%class%", info["class"])
	data = data.replace("%file%", info["file"])
	data = data.replace("%file_name%", get_path("name", info["file"]))
	data = data.replace("%package_path%", info["package"])
	data = data.replace("%visibility%", info["visibility"])
	if classType == "Class":
		data = data.replace("%modifier%", info["modifier"])
	data = data.replace("%inheritance%", inheritance)
	data = data.replace("%body%", info["body"])
	return data


def insert_and_save(view, contents, info):
	view.run_command("insert_snippet", {"contents": contents})
	if not is_stable() and (info["extends"] != "" or len(info["implements"]) > 0):
		view.run_command("javatar_organize_imports")
	view.run_command("save")


def create_class_file(file_path, contents, msg, info):
	if contents is None:
		return
	if os.path.exists(file_path):
		sublime.error_message(msg)
		return
	open(file_path, "w")
	view = sublime.active_window().open_file(file_path)
	view.set_syntax_file("Packages/Java/Java.tmLanguage")
	sublime.set_timeout(lambda: insert_and_save(view, contents, info), 100)


class JavatarCreateCommand(sublime_plugin.WindowCommand):
	def run(self, text="", create_type=""):
		get_action().add_action("javatar.command.create.run", "Create [create_type=" + create_type + "]")
		if create_type != "":
			self.show_input(-1, create_type)
			return
		if text != "":
			info = get_info(text)
			get_action().add_action("javatar.command.create.run", "Create [info=" + str(info) + "]")
			create_class_file(info["file"], get_file_contents(self.create_type, info), self.create_type + "\"" + info["class"] + "\" already exists", info)
			sublime.set_timeout(lambda: show_status(self.create_type + " \"" + info["class"] + "\" is created within package \"" + to_readable_package(info["package"], True) + "\""), 500)

	def show_input(self, index, create_type=""):
		if create_type != "" or index >= 0:
			if create_type != "":
				self.create_type = create_type
			else:
				self.create_type = get_snippet_name(index)
			sublime.active_window().show_input_panel(self.create_type + " Name:", "", self.run, "", "")
