import os
import re
import sublime


SNIPPETS = []


def analyseSnippet(file):
    f = open(file, "r")
    data = f.read()
    classScope = None
    classRe = re.search("%class:(.*)%(\\s*)", data, re.I | re.M)
    if classRe is not None:
        classScope = classRe.group(0)
        data = re.sub("%class:(.*)%(\\s*)", "", data)
        classScope = re.sub("(\\s*)$", "", classScope)
        classScope = classScope[7:-1]

    if classScope is None or classScope == "":
        from .javatar_utils import getPath
        classScope = getPath("name", file)[:-8]

    descriptionScope = ""
    descriptionRe = re.search("%description:(.*)%(\\s*)", data, re.I | re.M)
    if descriptionRe is not None:
        descriptionScope = descriptionRe.group(0)
        data = re.sub("%description:(.*)%(\\s*)", "", data)
        descriptionScope = re.sub("(\\s*)$", "", descriptionScope)
        descriptionScope = descriptionScope[13:-1]
    return {"file": file, "class": classScope, "description": descriptionScope, "data": data}


def getSnippetFiles():
    for root, dirnames, filenames in os.walk(sublime.packages_path()):
        for filename in filenames:
            if filename.endswith(".javatar"):
                print("Javatar Snippet " + filename + " loaded")
                SNIPPETS.append(analyseSnippet(os.path.join(root, filename)))


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
