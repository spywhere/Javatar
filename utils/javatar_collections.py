import re
import sublime
from .javatar_actions import *


SNIPPETS = []
DEFAULTIMPORTS = []

'''
Allow to include a javatar-packages files into project (atleast easier for bukkit autocomplete)
Allow a new javatar format for packaging a custom jar file (atleast easier for bukkit plugin jar file)
'''

def resetSnippetsAndImports():
	getAction().addAction("javatar.util.collection.reset", "Reset all snippets and default imports")
	global SNIPPETS, DEFAULTIMPORTS
	SNIPPETS = []
	DEFAULTIMPORTS = []


def analyseSnippet(file):
	getAction().addAction("javatar.util.collection.analyse_snippet", "Analyse snippet [file="+file+"]")
	data = sublime.load_resource(file)
	classScope = None
	classRe = re.search("%class:(.*)%(\\s*)", data, re.M)
	if classRe is not None:
		classScope = classRe.group(0)
		data = re.sub("%class:(.*)%(\\s*)", "", data)
		classScope = re.sub("(\\s*)$", "", classScope)
		classScope = classScope[7:-1]

	if classScope is None or classScope == "":
		from .javatar_utils import getPath
		classScope = getPath("name", file)[:-8]

	descriptionScope = ""
	descriptionRe = re.search("%description:(.*)%(\\s*)", data, re.M)
	if descriptionRe is not None:
		descriptionScope = descriptionRe.group(0)
		data = re.sub("%description:(.*)%(\\s*)", "", data)
		descriptionScope = re.sub("(\\s*)$", "", descriptionScope)
		descriptionScope = descriptionScope[13:-1]
	return {"file": file, "class": classScope, "description": descriptionScope, "data": data}


def getSnippetFiles():
	getAction().addAction("javatar.util.collection.get_snippet_files", "Load snippets")
	from .javatar_utils import getPath
	for filepath in sublime.find_resources("*.javatar"):
		filename = getPath("name", filepath)
		getAction().addAction("javatar.util.collection", "Javatar Snippet " + filename + " loaded")
		print("Javatar Snippet " + filename + " loaded")
		SNIPPETS.append(analyseSnippet(filepath))


def countImports(imports):
	packages = 0
	classes = 0
	if "packages" in imports:
		for packageName in imports["packages"]:
			package = imports["packages"][packageName]
			packages += 1
			if "interface" in package:
				classes += len(package["interface"])
			if "class" in package:
				classes += len(package["class"])
			if "enum" in package:
				classes += len(package["enum"])
			if "exception" in package:
				classes += len(package["exception"])
			if "error" in package:
				classes += len(package["error"])
			if "annotation" in package:
				classes += len(package["annotation"])
			if "type" in package:
				classes += len(package["type"])
	return [packages, classes]


def analyseImport(file):
	getAction().addAction("javatar.util.collection.analyse_import", "Analyse import [file="+file+"]")
	try:
		from .javatar_utils import getPath
		imports = sublime.decode_value(sublime.load_resource(file))
		if "experiment" in imports and imports["experiment"]:
			return None
		filename = getPath("name", file)
		if "name" in imports:
			filename = imports["name"]
		count = countImports(imports)
		print("Javatar Packages \"" + filename + "\" loaded with " + str(count[1]) + " classes in " + str(count[0]) + " packages")
		return imports
	except ValueError:
		sublime.error_message("Invalid JSON format")
	return None

def getImportFiles():
	global DEFAULTIMPORTS
	getAction().addAction("javatar.util.collection.get_import_files", "Load Java default imports")
	from .javatar_utils import getPath, isStable
	if not isStable():
		for filepath in sublime.find_resources("*.javatar-packages"):
			filename = getPath("name", filepath)
			getAction().addAction("javatar.util.collection", "Javatar Default Imports " + filename + " loaded")
			imports = analyseImport(filepath)
			if imports is not None:
				DEFAULTIMPORTS.append(imports)

def getImports():
	imports = []
	for imp in DEFAULTIMPORTS:
		imports.append(imp)
	return imports

def getSnippet(name):
	for snippet in SNIPPETS:
		if snippet["class"] == name:
			return snippet["data"]
	return None


def getSnippetName(index):
	return SNIPPETS[index]["class"]


def getSnippetList():
	slist = []
	for snippet in SNIPPETS:
		slist.append([snippet["class"], snippet["description"]])
	return slist
