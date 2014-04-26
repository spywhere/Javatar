import sublime
import os
from .javatar_actions import *


STATUS = "Javatar"
SETTINGSBASE = None
SETTINGS = None


def reset():
	get_action().add_action("javatar.util.util.reset", "Reset all settings")
	global SETTINGS, SETTINGSBASE
	SETTINGS = None
	SETTINGSBASE = None
	from .javatar_collections import reset_snippets_and_packages
	reset_snippets_and_packages()


def isReady():
	return SETTINGS is not None


def read_settings(config):
	get_action().add_action("javatar.util.util.read_settings", "Read settings")
	global SETTINGS, SETTINGSBASE
	SETTINGSBASE = config
	SETTINGS = sublime.load_settings(config)
	from .javatar_collections import load_snippets_and_packages
	load_snippets_and_packages()


def get_project_settings(key, asList=False):
	project_data = sublime.active_window().project_data()
	if key in project_data:
		if asList:
			return [project_data[key], True]
		else:
			return project_data[key]
	return None


def get_global_settings(key, asList=False):
	if asList:
		return [SETTINGS.get(key, None), False]
	else:
		return SETTINGS.get(key, None)


def get_settings(key, asList=False):
	project_settings = get_project_settings(key, asList)
	if project_settings is not None:
		return project_settings
	return get_global_settings(key, asList)


def set_settings(key, val, project=False):
	if project:
		project_data = sublime.active_window().project_data()
		project_data[key] = val
		sublime.active_window().set_project_data(project_data)
	else:
		SETTINGS.set(key, val)
		sublime.save_settings(SETTINGSBASE)


def is_debug():
	return get_settings("debug_mode")


def is_stable():
	return str.lower(get_settings("package_channel")) != "dev"


def normalize_path(path):
	name = get_path("name", path)
	parent = get_path("parent", path)
	if parent != get_path("parent", parent):
		parent = normalize_path(parent)
	for dir_path in os.listdir(parent):
		if dir_path.lower() == name:
			return get_path("join", parent, dir_path)
	return path


def split_path(path):
	rest, tail = os.path.split(path)
	if len(rest) <= 1:
		return tail,
	return split_path(rest) + (tail,)


def join_path(paths):
	outpath = ""
	for path in paths:
		outpath = os.path.join(outpath, path)
	return outpath


def merge_path(pathlist):
	outpath = ""
	for path in pathlist:
		outpath = get_path("join", outpath, path)
	return outpath


def show_status(text, delay=None, require_java=True):
	if delay is None:
		delay = get_settings("status_delay")
	from .javatar_validator import is_java
	if not is_java() and require_java:
		return
	view = sublime.active_window().active_view()
	view.set_status(STATUS, text)
	if delay >= 0:
		sublime.set_timeout(hide_status, delay)


def hide_status():
	view = sublime.active_window().active_view()
	if view is not None:
		from .javatar_validator import is_java
		if isReady() and is_java() and get_settings("show_package_path"):
			view.set_status(STATUS, "Package: " + to_readable_package(get_current_package(), True))
		else:
			view.erase_status(STATUS)


def to_readable_size(filepath):
	if filepath[0:8] == "Packages":
		filepath = sublime.packages_path()+filepath[8:]
	scales = [
		[1000**5, "PB"],
		[1000**4, "TB"],
		[1000**3, "GB"],
		[1000**2, "MB"],
		[1000**1, "KB"],
		[1000**0, "B"]
	]
	filesize = os.path.getsize(filepath)
	for scale in scales:
		if filesize >= scale[0]:
			break
	return str(int(filesize/scale[0]*100)/100)+scale[1]


def get_current_package(relative=False):
	from .javatar_validator import is_project, is_file
	if not relative and is_file() and get_path("current_dir") is not None:
		return to_package(get_path("current_dir"))
	elif not relative and is_project() and get_path("source_folder") is not None:
		return to_package(get_path("source_folder"))
	else:
		return ""


def to_readable_package(package, asPackage=False):
	if not asPackage:
		package = to_package(package)
	if package == "":
		from .javatar_validator import is_project
		if is_project():
			package = "(Default Package)"
		else:
			package = "(Unknown Package)"
	return package


def to_package(path, relative=True):
	if relative:
		path = get_path("relative", path, get_package_root_dir())
	package = ".".join(split_path(path))
	from .javatar_java import normalize_package
	return normalize_package(package)


def get_package_root_dir(isSub=False):
	from .javatar_validator import is_project, is_file
	if is_project() and not isSub:
		return get_path("source_folder")
	elif is_file() and isSub:
		return get_path("current_dir")
	elif get_path("current_dir") is not None:
		return get_path("current_dir")
	else:
		return ""


def contains_file(directory, file_path):
	return os.path.normcase(os.path.normpath(file_path)).startswith(os.path.normcase(os.path.normpath(directory)))


def without_extension(file_path):
	for extension in get_settings("java_extensions"):
		if file_path.endswith("."+extension):
			return file_path[:-len(extension)-1]
	return file_path


def get_class_name(file_path=None, view=None):
	from .javatar_validator import is_file
	if view is not None:
		classRegions = view.find_by_selector(get_settings("class_name_selector"))
		if len(classRegions) > 0:
			return view.substr(classRegions[0])
		else:
			return without_extension(get_path("name", view.file_name()))
	elif file_path is not None:
		return without_extension(get_path("name", file_path))
	else:
		if is_file():
			return get_class_name(None, sublime.active_window().active_view())
	return None


def parse_macro(text, macro_data=None, file_path=None):
	if file_path is not None:
		text = text.replace("$file_parent", get_path("parent", file_path))
		text = text.replace("$file_name", get_path("name", file_path))
		text = text.replace("$file", file_path)
	if macro_data is not None:
		for key in macro_data:
			text = text.replace("$"+key, macro_data[key])
	return text


def get_macro_data():
	from .javatar_java import normalize_package
	from .javatar_validator import is_file
	source_data = {}
	source_data["project_dir"] = get_path("project_dir")
	source_data["source_folder"] = get_path("source_folder")
	source_data["packages_path"] = sublime.packages_path()
	source_data["sep"] = os.sep
	if is_file():
		source_data["full_class_path"] = normalize_package(get_current_package()+"."+get_class_name())
		source_data["class_name"] = get_class_name()
		source_data["package"] = get_current_package()
	return source_data


def get_path(path_type="", dir_path="", dir_path2=""):
	window = sublime.active_window()
	if path_type == "source_folder":
		from .javatar_validator import is_file
		path = get_settings("source_folder")
		if path != "":
			return path
		if path is None:
			path = ""
		folders = window.folders()
		if len(folders) == 1:
			return folders[0]
		for folder in folders:
			if is_file() and contains_file(folder, get_path("current_file")):
				path = folder
				break
		return path
	elif path_type == "project_dir":
		folders = window.folders()
		if len(folders) == 1:
			return folders[0]
		elif len(folders) > 1:
			return get_path("parent", folders[0])
		for folder in folders:
			if is_file() and contains_file(folder, get_path("current_file")):
				return folder
				break
		return ""
	elif path_type == "current_dir":
		if get_path("current_file") is not None:
			return get_path("parent", get_path("current_file"))
		else:
			return None
	elif path_type == "current_file":
		return window.active_view().file_name()
	elif path_type == "parent":
		return os.path.dirname(dir_path)
	elif path_type == "relative":
		if dir_path != "" and dir_path2 != "":
			return os.path.relpath(dir_path, dir_path2)
		else:
			return ""
	elif path_type == "name":
		return os.path.basename(dir_path)
	elif path_type == "join":
		return os.path.join(dir_path, dir_path2)
	elif path_type == "exist":
		return os.path.exists(dir_path)
	elif path_type == "javatar_parent":
		name = __name__.split('.')
		return name[0]
	else:
		return ""
