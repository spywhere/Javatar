import os
from os.path import join, relpath, basename
import sublime
import sublime_plugin
from ..utils import *


def get_info(text, on_change=False):
    relative = True
    if text.startswith("~"):
        text = text[1:]
        relative = False

    if not is_project() and not (is_project() and is_file()):
        if on_change:
            return "Cannot specify package location"
        sublime.error_message("Cannot specify package location")
        return
    if not is_package(text, True):
        if on_change:
            return "Invalid package naming"
        sublime.error_message("Invalid package naming")
        return
    if relative and get_current_dir() is not None:
        create_directory = join(get_current_dir(), package_as_directory(get_package_path(text)))
    else:
        create_directory = join(get_package_root_dir(), package_as_directory(get_package_path(text)))

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
    visibility_keyword = "public"
    visibility = visibilityMap[visibility_keyword]
    modifier_keyword = ""
    modifier = ""
    extends = []
    implements = []
    package = to_package(relpath(create_directory, get_package_root_dir()), False)
    if not on_change:
        make_package(create_directory, True)
    className = get_class_name_by_regex(text)

    for visibilityKeyword, visibilityCode in visibilityMap.items():
        if className.lower().startswith(visibilityKeyword):
            className = className[len(visibilityKeyword):]
            visibility_keyword = visibilityKeyword
            visibility = visibilityCode
            break

    for modifierKeyword, modifierCode in modifierMap.items():
        if className.lower().startswith(modifierKeyword):
            className = className[len(modifierKeyword):]
            modifier_keyword = modifierKeyword
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

    asmain = False
    if className.lower().endswith("asmain"):
        asmain = True
        className = className[:-6]
        body = "public static void main(String[] args) {\n\t\t${1}\n\t}"

    file_path = join(create_directory, className + ".java")
    return {"file": file_path, "package": package, "visibility_keyword": visibility_keyword, "visibility": visibility, "modifier_keyword": modifier_keyword, "modifier": modifier, "class": className, "extends": extends, "implements": implements, "body": body, "asmain": asmain}


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
    if classType != "Enumerator" and len(info["extends"]) > 0:
        if classType == "Class" and len(info["extends"]) > 1:
            inheritance = " extends " + info["extends"][0]
        else:
            inheritance = " extends " + ", ".join(info["extends"])
    if classType != "Interface" and len(info["implements"]) > 0:
        inheritance += " implements " + ", ".join(info["implements"])

    data = data.replace("%class%", info["class"])
    data = data.replace("%file%", info["file"])
    data = data.replace("%file_name%", basename(info["file"]))
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
    def run(self, text="", create_type="", on_change=False):
        if on_change:
            if text == "":
                return get_info(text, on_change)
        else:
            add_action("javatar.command.create.run", "Create [create_type=" + create_type + "]")
        if create_type != "":
            self.show_input(-1, create_type)
            return
        if text != "":
            info = get_info(text, on_change)
            if on_change:
                if type(info) is str and info != "":
                    return info
                elif os.path.exists(info["file"]):
                    return self.create_type + " \"" + info["class"] + "\" already exists"
                else:
                    prefix = ""
                    additional_text = ""
                    if info["visibility_keyword"] != "":
                        prefix += info["visibility_keyword"]
                    if info["modifier_keyword"] != "":
                        prefix += " " + info["modifier_keyword"]
                    if info["asmain"]:
                        prefix += " main"
                    prefix += " " + self.create_type
                    prefix = prefix[:1].upper() + prefix[1:].lower()

                    if len(info["extends"]) > 2:
                        additional_text += ", extends \"" + "\", \"".join(info["extends"][:2]) + "\" and " + str(len(info["extends"]) - 2) + " more classes"
                    elif len(info["extends"]) > 0:
                        additional_text += ", extends \"" + "\", \"".join(info["extends"]) + "\""
                    if len(info["implements"]) > 2:
                        additional_text += ", implements \"" + "\", \"".join(info["implements"][:2]) + "\" and " + str(len(info["implements"]) - 2) + " more classes"
                    elif len(info["implements"]) > 0:
                        additional_text += ", implements \"" + "\", \"".join(info["implements"]) + "\""

                    if self.create_type == "Class" and len(info["extends"]) > 1:
                        additional_text += " [Warning! Class can be extent only once]"
                    elif self.create_type == "Enumerator" and len(info["extends"]) > 0:
                        additional_text += " [Warning! Enumerator use \"implements\" instead of \"extends\"]"
                    elif self.create_type == "Interface" and len(info["implements"]) > 0:
                        additional_text += " [Warning! Interface use \"extends\" instead of \"implements\"]"
                    return prefix + " \"" + info["class"] + "\" will be created within package \"" + to_readable_package(info["package"], True) + "\"" + additional_text
            add_action("javatar.command.create.run", "Create [info=" + str(info) + "]")
            create_class_file(info["file"], get_file_contents(self.create_type, info), self.create_type + " \"" + info["class"] + "\" already exists", info)
            sublime.set_timeout(lambda: show_status(self.create_type + " \"" + info["class"] + "\" is created within package \"" + to_readable_package(info["package"], True) + "\""), 500)

    def on_change(self, text):
        show_status(self.run(text, on_change=True), delay=-1, require_java=False)

    def on_cancel(self):
        hide_status(clear=True)

    def show_input(self, index, create_type=""):
        if create_type != "" or index >= 0:
            if create_type != "":
                self.create_type = create_type
            else:
                self.create_type = get_snippet_name(index)
            sublime.active_window().show_input_panel(self.create_type + " Name:", "", self.run, self.on_change, self.on_cancel)
