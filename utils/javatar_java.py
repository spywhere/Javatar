import os
import re
import sublime


def normalizePackage(package):
	while package.startswith("."):
		package = package[1:]
	return re.sub("\\.*$", "", package)


def getAllTypes(packageImports):
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
	return imports


def findClass(path, classname):
	from .javatar_utils import toPackage, getSettings
	from .javatar_collections import getImports
	classes = []
	foundClass = False
	for root, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename == classname + ".java":
				classpath = toPackage(os.path.join(root, filename)[:-5])
				classes.append(classpath)
				foundClass = True
	for packageImport in getSettings("default_import"):
		if foundClass and "default" in packageImport and packageImport["default"]:
			continue
		if classname in getAllTypes(packageImport):
			if packageImport["package"] != "" and packageImport["package"] not in classes and ("default" not in packageImport or not packageImport["default"]):
				classes.append(packageImport["package"]+"."+classname)
	for packageImport in getImports():
		if foundClass and "default" in packageImport and packageImport["default"]:
			continue
		if classname in getAllTypes(packageImport):
			if packageImport["package"] != "" and packageImport["package"] not in classes and ("default" not in packageImport or not packageImport["default"]):
				classes.append(packageImport["package"]+"."+classname)
	classes.sort()
	return classes


def getPackagePath(text):
	from .javatar_utils import getSettings
	return normalizePackage(re.search(getSettings("package_match"), text, re.M).group(0))


def getClassName(text):
	from .javatar_utils import getSettings
	return re.search(getSettings("package_class_match"), text, re.M).group(0)


def packageAsDirectory(package):
	from .javatar_utils import mergePath
	return mergePath(package.split("."))


def makePackage(current_dir, package, silent=False):
	from .javatar_utils import getPath
	target_dir = getPath("join", current_dir, packageAsDirectory(package))
	if not os.path.exists(target_dir):
		try:
			os.makedirs(target_dir)
		except BaseException as e:
			sublime.error_message("Error while create a package: " + str(e))
	else:
		if not silent:
			sublime.message_dialog("Package is already exists")
	return target_dir
