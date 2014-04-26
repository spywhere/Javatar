import os
import re
import sublime


def normalize_package(package):
	while package.startswith("."):
		package = package[1:]
	return re.sub("\\.*$", "", package)


def get_all_types(packageImports):
	imports = []
	if "package" in packageImports:
		if "interface" in packageImports:
			imports += packageImports["interface"]
		if "class" in packageImports:
			imports += packageImports["class"]
		if "enum" in packageImports:
			imports += packageImports["enum"]
		if "exception" in packageImports:
			imports += packageImports["exception"]
		if "error" in packageImports:
			imports += packageImports["error"]
		if "type" in packageImports:
			imports += packageImports["type"]
		if "annotation" in packageImports:
			imports += packageImports["annotation"]
	else:
		if "interface" in packageImports:
			for interface in packageImports["interface"]:
				imports.append(interface["name"])
		if "class" in packageImports:
			for clazz in packageImports["class"]:
				imports.append(clazz["name"])
		if "enum" in packageImports:
			for enum in packageImports["enum"]:
				imports.append(enum["name"])
		if "exception" in packageImports:
			for exception in packageImports["exception"]:
				imports.append(exception["name"])
		if "error" in packageImports:
			for error in packageImports["error"]:
				imports.append(error["name"])
		if "type" in packageImports:
			for types in packageImports["type"]:
				imports.append(types["name"])
		if "annotation" in packageImports:
			for annotation in packageImports["annotation"]:
				imports.append(annotation["name"])
	return imports


def find_class(path, classname):
	# If it is a default class, should import manually
	from .javatar_utils import to_package, get_settings, without_extension
	from .javatar_collections import get_packages
	classes = []
	foundClass = False
	for root, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename == classname + ".java":
				classpath = to_package(without_extension(os.path.join(root, filename)))
				classes.append(classpath)
				foundClass = True
	for packageImport in get_packages():
		if "packages" in packageImport:
			for packageName in packageImport["packages"]:
				package = packageImport["packages"][packageName]
				if not foundClass and "default" in package and package["default"]:
					continue
				if classname in get_all_types(package):
					classes.append(packageName+"."+classname)
	classes.sort()
	return classes


def get_package_path(text):
	from .javatar_utils import get_settings
	return normalize_package(re.search(get_settings("package_match"), text, re.M).group(0))


def get_class_name_by_regex(text):
	from .javatar_utils import get_settings
	return re.search(get_settings("package_class_match"), text, re.M).group(0)


def package_as_directory(package):
	from .javatar_utils import merge_path
	return merge_path(package.split("."))


def make_package(current_dir, package, silent=False):
	from .javatar_utils import get_path
	target_dir = get_path("join", current_dir, package_as_directory(package))
	if not os.path.exists(target_dir):
		try:
			os.makedirs(target_dir)
		except BaseException as e:
			sublime.error_message("Error while create a package: " + str(e))
	else:
		if not silent:
			sublime.message_dialog("Package is already exists")
	return target_dir
