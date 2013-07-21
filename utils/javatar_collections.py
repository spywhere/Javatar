import os
import sublime


SNIPPETS = []


def getSnippetFiles():
    for root, dirnames, filenames in os.walk(sublime.packages_path()):
        for filename in filenames:
            if filename.endswith(".javatar"):
                print("Javatar Snippet " + filename + " loaded")
                SNIPPETS.append({"name": filename[:-8], "path": os.path.join(root, filename)})


def getSnippet(name):
    for snippet in SNIPPETS:
        if snippet["name"] == name:
            return snippet["path"]
    return ""


def getSnippetName(index):
    return SNIPPETS[index]["name"]


def getSnippetList():
    slist = []
    for snippet in SNIPPETS:
        slist.append(snippet["name"])
    return slist
