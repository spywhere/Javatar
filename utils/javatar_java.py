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


def findClass(path, classname):
	# If it is a default class, should import manually
	from .javatar_utils import toPackage, getSettings
	from .javatar_collections import getPackages
	classes = []
	foundClass = False
	for root, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename == classname + ".java":
				classpath = toPackage(withoutExtension(os.path.join(root, filename)))
				classes.append(classpath)
				foundClass = True
	for packageImport in getPackages():
		if "packages" in packageImport:
			for packageName in packageImport["packages"]:
				package = packageImport["packages"][packageName]
				if not foundClass and "default" in package and package["default"]:
					continue
				if classname in getAllTypes(package):
					classes.append(packageName+"."+classname)
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
