import os
import re
from os.path import join, relpath, basename
import sublime
import sublime_plugin
from ..utils import (
    get_snippet,
    hide_status,
    add_action,
    is_stable,
    get_snippet_name,
    show_status,
    to_readable_package,
    get_class_name_by_regex,
    get_package_root_dir,
    to_package,
    is_project,
    package_as_directory,
    is_file,
    get_package_path,
    is_package,
    make_package,
    get_current_dir
)

EXTENDS_IMPLEMENTS_RE = re.compile(r'([:<])')
MAIN_TEMPLATE = "public static void main(String[] args) {\n\t\t${1}\n\t}"
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


def find_keyword(className, Map):
    for keyword, code in Map.items():
        if className.lower().startswith(keyword):
            className = className[len(keyword):]

            return className, keyword, code

    return className, None, None


def parse_spec(text):
    relative = True
    if text.startswith("~"):
        text = text[1:]
        relative = False

    className = get_class_name_by_regex(text)

    className, visibility_keyword, visibility = find_keyword(className, visibilityMap)
    className, modifier_keyword, modifier = find_keyword(className, modifierMap)
    modifier = modifier or ""
    modifier_keyword = modifier_keyword or ""
    visibility_keyword = visibility_keyword or "public"
    visibility = visibility or visibilityMap[visibility_keyword]

    parts = EXTENDS_IMPLEMENTS_RE.split(className)

    extends = []
    implements = []
    className = parts.pop(0)
    while parts:
        part = parts.pop(0)
        if part == '<':
            implements = parts.pop(0).split(',')
        elif part == ':':
            extends = parts.pop(0).split(',')

    asmain = False
    if className.lower().endswith("asmain"):
        asmain = True
        className = className[:-6]
        body = MAIN_TEMPLATE
    else:
        body = "${1}"

    return {
        'relative': relative,
        'className': className,
        'asmain': asmain,
        'body': body,
        'implements': implements,
        'extends': extends,
        'visibility_keyword': visibility_keyword,
        'visibility': visibility,
        'modifier_keyword': modifier_keyword,
        'modifier': modifier
    }


def get_info(text, on_change=False):
    if not is_project() and not (is_project() and is_file()):
        if on_change:
            return "Cannot specify package location"
        sublime.error_message("Cannot specify package location")
        return

    if not is_package(text.strip('~'), True):
        if on_change:
            return "Invalid package naming"
        sublime.error_message("Invalid package naming")
        return

    spec = parse_spec(text)

    text = text.strip('~')

    if spec['relative'] and get_current_dir() is not None:
        create_directory = join(get_current_dir(), package_as_directory(get_package_path(text)))
    else:
        create_directory = join(get_package_root_dir(), package_as_directory(get_package_path(text)))

    package = to_package(relpath(create_directory, get_package_root_dir()), False)
    if not on_change:
        make_package(create_directory, True)

    file_path = join(create_directory, spec['className'] + ".java")
    return {
        "file": file_path,
        "package": package,
        "visibility_keyword": spec['visibility_keyword'],
        "visibility": spec['visibility'],
        "modifier_keyword": spec['modifier_keyword'],
        "modifier": spec['modifier'],
        "class": spec['className'],
        "extends": spec['extends'],
        "implements": spec['implements'],
        "body": spec['body'],
        "asmain": spec['asmain']
    }


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

    data = (
        data.replace("%class%", info["class"])
            .replace("%file%", info["file"])
            .replace("%file_name%", basename(info["file"]))
            .replace("%package_path%", info["package"])
            .replace("%visibility%", info["visibility"])
            .replace("%inheritance%", inheritance)
            .replace("%body%", info["body"])
    )

    if classType == "Class":
        data = data.replace("%modifier%", info["modifier"])

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
        if on_change and text == "":
            return get_info(text, on_change)
        else:
            add_action("javatar.command.create.run", "Create [create_type=" + create_type + "]")

        if create_type != "":
            self.show_input(-1, create_type)
            return

        if text == "":
            return

        info = get_info(text, on_change)
        if on_change:
            if type(info) is str and info != "":
                return info
            elif os.path.exists(info["file"]):
                return self.create_type + " \"" + info["class"] + "\" already exists"
            else:
                prefix = self.build_prefix(info)
                additional_text = self.build_additional_text(info)
                return prefix + " \"" + info["class"] + "\" will be created within package \"" + to_readable_package(info["package"], True) + "\"" + additional_text

        add_action("javatar.command.create.run", "Create [info=" + str(info) + "]")
        create_class_file(info["file"], get_file_contents(self.create_type, info), self.create_type + " \"" + info["class"] + "\" already exists", info)
        sublime.set_timeout(lambda: show_status(self.create_type + " \"" + info["class"] + "\" is created within package \"" + to_readable_package(info["package"], True) + "\""), 500)

    def build_prefix(self, info):
        prefix = ""
        if info["visibility_keyword"] != "":
            prefix += info["visibility_keyword"]
        if info["modifier_keyword"] != "":
            prefix += " " + info["modifier_keyword"]
        if info["asmain"]:
            prefix += " main"
        prefix += " " + self.create_type

        return prefix[:1].upper() + prefix[1:].lower()

    def quote_list(self, lst):
        return ', '.join(
            '"{}"'.format(item)
            for item in lst
        )

    def build_additional_text(self, info):
        additional_text = ""

        if info["extends"]:
            additional_text += ", extends " + self.quote_list(info["extends"][:2])

            if len(info["extends"]) > 2:
                additional_text += " and {} more classes".format(len(info["extends"]) - 2)

        if info["implements"]:
            additional_text += ", implements " + self.quote_list(info["implements"][:2])

            if len(info["implements"]) > 2:
                additional_text += " and {} more classes".format(len(info["implements"]) - 2)

        if self.create_type == "Class" and len(info["extends"]) > 1:
            additional_text += " [Warning! Class can be extent only once]"

        elif self.create_type == "Enumerator" and info["extends"]:
            additional_text += ' [Warning! Enumerator use "implements" instead of "extends"]'

        elif self.create_type == "Interface" and info["implements"]:
            additional_text += ' [Warning! Interface use "extends" instead of "implements"]'

        return additional_text

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
