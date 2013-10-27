import os
import re
import sublime


def normalizePackage(package):
	while package.startswith("."):
		package = package[1:]
	return re.sub("\\.*$", "", package)


def findClass(path, classname):
	from .javatar_utils import toPackage, getPath, getSettings
	from .javatar_collections import getImports
	classes = []
	for root, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename == classname + ".java":
				classpath = toPackage(os.path.join(root, filename)[:-5])
				classes.append(classpath)
	for packageImport in getSettings("default_import"):
		if "type" in packageImport and "package" in packageImport:
			if classname in packageImport["type"]:
				if packageImport["package"] != "" and packageImport["package"] not in classes:
					classes.append(packageImport["package"]+"."+classname)
	for packageImport in getImports():
		if "type" in packageImport and "package" in packageImport:
			if classname in packageImport["type"]:
				if packageImport["package"] != "" and packageImport["package"] not in classes:
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
