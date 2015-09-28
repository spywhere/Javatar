import sublime
import sublime_plugin
import sys
from imp import reload
import hashlib
from ..parser.GrammarParser import GrammarParser
from ..core import (
    ActionHistory,
    JavaStructure,
    JSONPanel,
    Logger,
    StatusManager
)
from ..utils import (
    Constant,
    Downloader
)


class JavatarUtilsCommand(sublime_plugin.TextCommand):

    """
    Command for utility actions
    """

    def on_done(self, obj):
        """
        JSONPanel's on_done
        """
        Logger().none(str(sublime.encode_value(obj)))

    def on_cancel(self):
        """
        JSONPanel's on_cancel
        """
        Logger().none("Cancel")

    def run(self, edit, util_type="", text="", region=None, dest=None):
        """
        Run specified utility

        @param edit: edit object from Sublime Text buffer
        @param util_type: utility selector
        @param text: text to be used with edit object
        @param region: replace region (use with replace utility)
        @param dest: command description (use on dest method)
        """
        if util_type == "insert":
            self.view.insert(edit, 0, text)
        elif util_type == "add":
            self.view.insert(edit, self.view.size(), text)
        elif util_type == "replace":
            if isinstance(region, list) or isinstance(region, tuple):
                region = sublime.Region(region[0], region[1])
            self.view.replace(edit, region, text)
        elif util_type == "clear":
            self.view.erase(edit, sublime.Region(0, self.view.size()))
        elif util_type == "set_read_only":
            self.view.set_read_only(True)
        elif util_type == "clear_read_only":
            self.view.set_read_only(False)
        elif util_type == "parser_test" and Constant.is_debug():
            for cl in JavaStructure().classes_in_file(self.view.file_name()):
                print("Class: " + cl["name"])
                for ctor in JavaStructure().constructors_in_class(cl):
                    params = []
                    for param in ctor["params"]:
                        params.append(param["type"] + " " + param["name"])
                    print("  Constructor: " + ctor["name"] + "(" + ", ".join(params) + ")")
                for field in JavaStructure().fields_in_class(cl):
                    print("  Field: " + field["type"] + " " + field["name"])
                for method in JavaStructure().methods_in_class(cl):
                    params = []
                    for param in method["params"]:
                        params.append(param["type"] + " " + param["name"])
                    print("  Method: " + method["returnType"] + " " + method["name"] + "(" + ", ".join(params) + ")")
        elif util_type == "remote_hash":
            sublime.active_window().show_input_panel(
                "URL:", "", self.remote_hash, None, None
            )
        elif util_type == "hash":
            Logger().none(
                hashlib.sha256(
                    self.view.substr(
                        sublime.Region(0, self.view.size())
                    ).encode("utf-8")
                ).hexdigest()
            )
        elif util_type == "tojson":
            jsonObj = sublime.decode_value(
                self.view.substr(sublime.Region(0, self.view.size()))
            )
            self.view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                sublime.encode_value(jsonObj, True)
            )
        elif util_type == "json_test" and Constant.is_debug():
            panel = JSONPanel(
                window=self.view.window(),
                on_done=self.on_done,
                on_cancel=self.on_cancel
            )
            view = panel.open("JSONTest.json")
            sublime.set_timeout(
                lambda: view.run_command(
                    "javatar_utils", {"util_type": "insert", "text": "{\n}"}
                ),
                50
            )
        elif util_type == "parse":
            sublime.active_window().show_input_panel(
                "Parse Parameter:", "", self.parse_code, None, None
            )
        elif util_type == "reload" and Constant.is_debug():
            ActionHistory().add_action(
                "javatar.commands.utils.utils.reload", "Reload Javatar"
            )
            Logger().info("Reloading Javatar...")
            Constant.reset()
            for mod in tuple(sys.modules.keys()):
                if mod.lower().startswith("javatar"):
                    Logger().info("Reloading module " + mod + "...")
                    reload(sys.modules[mod])
            from ..Javatar import plugin_loaded
            plugin_loaded()

    def parse_code(self, selector):
        """
        Parse code against Java grammar

        @param selector: scope selector (refer to GrammarParser's selector)
        """
        try:
            scope = GrammarParser(sublime.decode_value(sublime.load_resource(
                "Packages/Javatar/grammars/Java8.javatar-grammar"
            )))
            parse_output = scope.parse_grammar(self.view.substr(
                sublime.Region(0, self.view.size())
            ))
            status_text = ""
            if parse_output["success"]:
                if selector == "":
                    nodes = scope.find_all()
                elif selector == "#":
                    selections = self.view.sel()
                    nodes = scope.find_by_region([0, 0])
                    if selections:
                        first_sel = selections[0]
                        if first_sel.empty():
                            nodes = scope.find_by_region(
                                [first_sel.begin(), first_sel.end()]
                            )
                        else:
                            nodes = scope.find_inside_region(
                                [first_sel.begin(), first_sel.end()]
                            )
                else:
                    nodes = scope.find_by_selectors(selector)
                if selector != "#":
                    status_text = "Parsing got {} tokens".format(len(nodes))
                for node in nodes:
                    if selector == "#":
                        if status_text == "":
                            status_text += node["name"]
                        else:
                            status_text += " " + node["name"]
                    else:
                        Logger().none(
                            "#{begin}:{end} => {name}".format_map(node)
                        )
                        Logger().none(
                            "   => {value}".format_map(node)
                        )

                Logger().none("Total: {} tokens".format(len(nodes)))
            if selector != "#":
                if (status_text != "" and
                        str(parse_output["end"]) == str(self.view.size())):
                    status_text += " in {elapse_time:.2f}s".format(
                        elapse_time=scope.get_elapse_time()
                    )
                else:
                    status_text = "Parsing failed [%s/%s] in {%.2f}s" % (
                        parse_output["end"],
                        self.view.size(),
                        scope.get_elapse_time()
                    )
            Logger().none(
                "Ending: %s/%s" % (parse_output["end"], self.view.size())
            )
            Logger().none(
                "Parsing Time: {elapse_time:.2f}s".format(
                    elapse_time=scope.get_elapse_time()
                )
            )
            StatusManager().show_status(status_text)
        except Exception as e:
            ActionHistory().add_action(
                "javatar.commands.utils.parse_code",
                "Error while parsing",
                e
            )

    def remote_hash(self, url):
        """
        Print hash of data from URL

        @param url: URL to fetch data
        """
        try:
            data = Downloader.download(url)
            datahash = hashlib.sha256(data).hexdigest()
            Logger().none("Hash: " + datahash)
        except Exception as e:
            ActionHistory().add_action(
                "javatar.commands.utils.remote_hash",
                "Error while remote hash",
                e
            )

    def nothing(self, index=-1):
        """
        Dummy method for testing test utility
        """
        pass

    def description(self, util_type="", text="", region=None, dest=None):
        """
        Returns command description (which will display on undo/redo menu)

        @params are same as run method except no edit argument
        """
        return dest


class JavatarViewCommand(sublime_plugin.WindowCommand):
    def run(self):
        group, index = self.window.get_view_index(self.window.active_view())
        if index < 0:
            print("Current view group is %s" % (group))
        else:
            print("Current view index is %s" % (index))
            print("Current view group is %s" % (group))
