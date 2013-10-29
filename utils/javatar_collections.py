import re
import sublime
from .javatar_actions import *


SNIPPETS = []
DEFAULTIMPORTS = []


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
	for imp in imports:
		if "package" in imp:
			packages += 1
			if "interface" in imp:
				classes += len(imp["interface"])
			if "class" in imp:
				classes += len(imp["class"])
			if "enum" in imp:
				classes += len(imp["enum"])
			if "exception" in imp:
				classes += len(imp["exception"])
			if "error" in imp:
				classes += len(imp["error"])
			if "annotation" in imp:
				classes += len(imp["annotation"])
			if "type" in imp:
				classes += len(imp["type"])
	return [packages, classes]


def analyseImport(file):
	getAction().addAction("javatar.util.collection.analyse_import", "Analyse import [file="+file+"]")
	try:
		from .javatar_utils import getPath
		imports = sublime.decode_value(sublime.load_resource(file))
		filename = getPath("name", file)
		count = countImports(imports)
		print("Javatar Imports " + filename + " loaded with " + str(count[1]) + " classes in " + str(count[0]) + " packages")
		return imports
	except ValueError:
		sublime.error_message("Invalid JSON format")
	return None

def getImportFiles():
	global DEFAULTIMPORTS
	getAction().addAction("javatar.util.collection.get_import_files", "Load Java default imports")
	from .javatar_utils import getPath
	for filepath in sublime.find_resources("*.javatar-imports"):
		filename = getPath("name", filepath)
		getAction().addAction("javatar.util.collection", "Javatar Default Imports " + filename + " loaded")
		imports = analyseImport(filepath)
		if imports is not None:
			DEFAULTIMPORTS += imports

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
