import sublime
import sublime_plugin
import os.path
from ..core import (
    JavaClass,
    JavaClassPath,
    JavaUtils,
    RE,
    StateProperty
)
from ..utils import (
    ActionHistory,
    StatusManager
)


EXTENDS_IMPLEMENTS_RE = "([:<])"
MAIN_TEMPLATE = "public static void main(String[] args) {\n\t\t${1}\n\t}"
VISIBILITY_MAP = {
    "public": "public ",
    "default": "",
    "private": "private ",
    "protected": "protected "
}
MODIFIER_MAP = {
    "abstract": "abstract ",
    "final": "final "
}


class JavatarCreateCommand(sublime_plugin.WindowCommand):

    """
    Command to show menu which use to create a new Java file
    """

    def find_keyword(self, jclass, keywords, default=None):
        """
        Returns a 3-tuple consists of (trimmed class, keyword, value) by
            remove the matched keyword

        @param jclass: a class path to trimmed
        @param keywords: a keyword dictionary
        @param default: a 2-tuple/list for default keyword and value when no
            keyword matched
        """
        default = default or (None, None)
        for key, value in keywords.items():
            if jclass.get().lower().startswith(key):
                return (JavaClass(jclass.get()[len(key):]), key, value)
        return (jclass,) + tuple(default)

    def parse_class_info(self, text):
        """
        Returns class informations by analyse the input text

        @param text: text to be analysed
        """
        relative_path = True
        if text.startswith("~"):
            text = text[1:]
            relative_path = False

        class_path = JavaClassPath(text)
        jclass = class_path.get_class()
        jclass, visibility_keyword, visibility = self.find_keyword(
            jclass,
            VISIBILITY_MAP,
            ["public", VISIBILITY_MAP["public"]]
        )
        jclass, modifier_keyword, modifier = self.find_keyword(
            jclass,
            MODIFIER_MAP,
            ["", ""]
        )

        class_name = jclass.get()
        parts = RE.get(
            "extends_implements",
            EXTENDS_IMPLEMENTS_RE
        ).split(class_name)

        extends = []
        implements = []
        class_name = parts.pop(0)
        while parts:
            part = parts.pop(0)
            if part == "<":
                implements = parts.pop(0).split(",")
            elif part == ":":
                extends = parts.pop(0).split(",")

        as_main = False
        if class_name.lower().endswith("asmain"):
            as_main = True
            class_name = class_name[:-6]
            body = MAIN_TEMPLATE
        else:
            body = "${1}"

        return {
            "relative_path": relative_path,
            "class_name": class_name,
            "package": class_path.get_package(),
            "as_main": as_main,
            "body": body,
            "implements": implements,
            "extends": extends,
            "visibility_keyword": visibility_keyword,
            "visibility": visibility,
            "modifier_keyword": modifier_keyword,
            "modifier": modifier
        }

    def parse_create(self, text):
        """
        If success, returns class informations, package path and file path
            from input text, otherwise, returns a string described an error

        @param text: text to be analysed
        """
        if not StateProperty.is_project() or not StateProperty.is_file():
            return "Cannot specify package location"
        if not JavaUtils.is_class_path(text.strip("~"), special=True):
            return "Invalid class naming"
        class_info = self.parse_class_info(text)
        if not class_info["class_name"]:
            return "Invalid class naming"

        if class_info["relative_path"] and StateProperty.get_dir():
            create_directory = os.path.join(
                StateProperty.get_dir(),
                class_info["package"].as_path()
            )
        else:
            create_directory = os.path.join(
                StateProperty.get_root_dir(),
                class_info["package"].as_path()
            )

        class_info["package"] = JavaUtils.to_package(create_directory)
        # JavaUtils.create_package_path(create_directory, True)
        class_info["file"] = os.path.join(
            create_directory,
            class_info["class_name"] + ".java"
        )
        return class_info

    def build_prefix(self, info):
        """
        Returns a string described the class that will be used as prefix

        @param info: class informations
        """
        prefix = ""
        if info["visibility_keyword"]:
            prefix += info["visibility_keyword"]
        if info["modifier_keyword"]:
            prefix += " " + info["modifier_keyword"]
        if info["as_main"]:
            prefix += " main"
        prefix += " " + self.args["create_type"]
        return prefix[:1].upper() + prefix[1:].lower()

    def quote_list(self, lst):
        """
        Returns a joined string which each item in the list got quoted

        @param lst: a list to be joined
        """
        return ", ".join(
            ["\"{}\"".format(item) for item in lst]
        )

    def build_additional_text(self, info):
        """
        Returns a string described additional class informations such as class
            inheritances or warnings that will be appended to the end of
            the line

        @param info: class informations
        """
        additional_text = ""

        if info["extends"]:
            additional_text += ", extends {}".format(
                self.quote_list(info["extends"][:2])
            )

            if len(info["extends"]) > 2:
                additional_text += " and {} more classes".format(
                    len(info["extends"]) - 2
                )

        if info["implements"]:
            additional_text += ", implements {}".format(
                self.quote_list(info["implements"][:2])
            )

            if len(info["implements"]) > 2:
                additional_text += " and {} more classes".format(
                    len(info["implements"]) - 2
                )

        if self.args["create_type"] == "Class" and len(info["extends"]) > 1:
            additional_text += " [Warning! Class can be extent only once]"

        elif self.args["create_type"] == "Enumerator" and info["extends"]:
            additional_text += (
                " [Warning! Enumerator use \"implements\"" +
                " instead of \"extends\"]"
            )

        elif self.args["create_type"] == "Interface" and info["implements"]:
            additional_text += (
                " [Warning! Interface use \"extends\"" +
                " instead of \"implements\"]"
            )

        return additional_text

    def on_done(self, text=""):
        """
        Create a class with informations from the input text

        @param text: text from input panel
        """
        pass

    def on_change(self, text=""):
        """
        Shows informations about how class get created in the status bar

        @param text: text from input panel
        """
        status = ""
        info = self.parse_create(text)
        if isinstance(info, str):
            status = info
        elif os.path.exists(info["file"]):
            status = "{create_type} \"{class_name}\" already exists".format_map(
                {
                    "create_type": self.args["create_type"],
                    "class_name": info["class_name"]
                }
            )
        else:
            prefix = self.build_prefix(info)
            status = "{prefix} \"{class_name}\" will be created".format_map({
                "prefix": prefix,
                "class_name": info["class_name"]
            })
            status += " within package \"{readable_package_path}\"".format_map({
                "readable_package_path": JavaUtils.to_readable_class_path(
                    info["package"].as_class_path(),
                    as_package=True
                )
            })
            status += " {additional_text}".format_map({
                "additional_text": self.build_additional_text(info)
            })
        StatusManager.show_status(
            status,
            delay=-1,
            ref="create_description"
        )

    def on_cancel(self):
        """
        Hides the text that is showed by on_change
        """
        StatusManager.hide_status("create_description")

    def run(self, create_type=None):
        """
        Create a specified Java file

        @param create_type: a snippet type to create
        """
        self.args = {
            "create_type": create_type
        }
        ActionHistory.add_action(
            "javatar.commands.create.run",
            "Create [create_type={create_type}]".format_map(self.args)
        )

        sublime.active_window().show_input_panel(
            "{create_type} Name:".format_map(self.args),
            "",
            self.on_done,
            self.on_change,
            self.on_cancel
        )
