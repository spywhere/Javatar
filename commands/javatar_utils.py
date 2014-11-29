import sys
from os.path import join, dirname, basename
from imp import reload

import sublime
import sublime_plugin
import hashlib
import urllib.request
import traceback
from ..parser.GrammarParser import GrammarParser
from ..utils import (
    is_stable, JSONPanel, is_debug, add_action, show_status,
    reset_packages, load_packages
)


class JavatarUtilCommand(sublime_plugin.TextCommand):
    def on_done(self, obj):
        print(str(sublime.encode_value(obj)))

    def on_cancel(self):
        print("Cancel")

    def run(self, edit, util_type="", text="", region=None, dest=None):
        if util_type == "insert":
            self.view.insert(edit, 0, text)
        elif util_type == "add":
            self.view.insert(edit, self.view.size(), text)
        elif util_type == "replace":
            self.view.insert(edit, region, text)
        elif util_type == "clear":
            self.view.erase(edit, sublime.Region(0, self.view.size()))
        elif util_type == "set_read_only":
            self.view.set_read_only(True)
        elif util_type == "clear_read_only":
            self.view.set_read_only(False)
        elif util_type == "test" and not is_stable():
            self.view.show_popup_menu(["A", "B"], self.nothing)
        elif util_type == "remote_hash" and not is_stable():
            sublime.active_window().show_input_panel("URL:", "", self.remote_hash, None, None)
        elif util_type == "hash" and not is_stable():
            print(hashlib.sha256(self.view.substr(sublime.Region(0, self.view.size())).encode("utf-8")).hexdigest())
        elif util_type == "tojson" and not is_stable():
            jsonObj = sublime.decode_value(self.view.substr(sublime.Region(0, self.view.size())))
            self.view.replace(edit, sublime.Region(0, self.view.size()), sublime.encode_value(jsonObj, True))
        elif util_type == "json_test" and not is_stable():
            panel = JSONPanel(window=self.view.window(), on_done=self.on_done, on_cancel=self.on_cancel)
            view = panel.open("JSONTest.json")
            sublime.set_timeout(lambda: view.run_command("javatar_util", {"util_type": "insert", "text": "{\n}"}), 50)
        elif util_type == "parse" and not is_stable():
            sublime.active_window().show_input_panel("Parse Parameter:", "", self.parse_code, None, None)
        elif util_type == "reload" and is_debug():
            add_action("javatar.command.utils.reload.run", "Reload Javatar")
            print("Reloading Javatar...")
            for mod in sys.modules:
                if mod.lower().startswith("javatar") and not mod.lower().endswith("_utils") and sys.modules[mod] is not None:
                    print("Reloading module " + mod + "...")
                    reload(sys.modules[mod])
            from ..Javatar import plugin_loaded
            plugin_loaded()

    def parse_code(self, text):
        try:
            grammars = sublime.find_resources("Java*.javatar-grammar")
            if len(grammars) > 0:
                scope = GrammarParser(sublime.decode_value(sublime.load_resource(grammars[0])))
                parse_output = scope.parse_grammar(self.view.substr(sublime.Region(0, self.view.size())))
                status_text = ""
                if parse_output["success"] and not is_stable():
                    if text == "":
                        nodes = scope.find_all()
                    elif text == "#":
                        selections = self.view.sel()
                        nodes = scope.find_by_region([0, 0])
                        if len(selections) > 0:
                            first_sel = selections[0]
                            if first_sel.empty():
                                nodes = scope.find_by_region([first_sel.begin(), first_sel.end()])
                            else:
                                nodes = scope.find_inside_region([first_sel.begin(), first_sel.end()])
                    else:
                        nodes = scope.find_by_selectors(text)
                    if text != "#":
                        status_text = "Parsing got " + str(len(nodes)) + " tokens"
                    for node in nodes:
                        if text == "#":
                            if status_text == "":
                                status_text += node["name"]
                            else:
                                status_text += " " + node["name"]
                        else:
                            print("#" + str(node["begin"]) + ":" + str(node["end"]) + " => " + node["name"])
                            print("   => " + node["value"])
                    print("Total: " + str(len(nodes)) + " tokens")
                if not is_stable():
                    if text != "#":
                        if status_text != "" and str(parse_output["end"]) == str(self.view.size()):
                            status_text += " in {elapse_time:.2f}s".format(elapse_time=scope.get_elapse_time())
                        else:
                            status_text = "Parsing failed [" + str(parse_output["end"]) + "/" + str(self.view.size()) + "] in {elapse_time:.2f}s".format(elapse_time=scope.get_elapse_time())
                    print("Ending: " + str(parse_output["end"]) + "/" + str(self.view.size()))
                    print("Parsing Time: {elapse_time:.2f}s".format(elapse_time=scope.get_elapse_time()))
                    show_status(status_text, None, False)
        except Exception:
            print("Error occurred while parsing")
            traceback.print_exc()

    def remote_hash(self, url):
        try:
            urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()))
            data = urllib.request.urlopen(url).read()
            datahash = hashlib.sha256(data).hexdigest()
            print("Hash: " + datahash)
        except Exception:
            print("Error occurred while remote_hash")
            traceback.print_exc()

    def nothing(self, index=-1):
        pass

    def description(self, util_type="", text="", dest=None):
        return dest


class JavatarReload_packagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        add_action(
            "javatar.command.utils.reload_packages.run", "Reload Packages"
        )
        reset_packages()
        load_packages()


class JavatarConvertCommand(sublime_plugin.WindowCommand):
    def run(self):
        for filepath in sublime.find_resources("*.javatar-imports"):
            add_action("javatar.command.utils.convert.run", "Converting imports \"" + basename(filepath) + "\"")
            packages_file = {"name": basename(filepath), "packages": {}}
            imports_file = sublime.decode_value(sublime.load_resource(filepath))
            total_package = 0
            total_class = 0
            for imports in imports_file:
                if "package" not in imports:
                    continue

                total_package += 1
                package = imports["package"]
                packages_file["packages"][package] = {}

                if "default" in imports:
                    packages_file["packages"][package]["default"] = imports["default"]

                to_include = {
                    "interface",
                    "class",
                    "enum",
                    "exception",
                    "error",
                    "annotation",
                    "type"
                }

                for key in to_include:
                    total_class += len(imports[key])
                    packages_file["packages"][package][key] = [
                        {"name": clss, "fields": [], "methods:": []}
                        for clss in imports[key]
                    ]

            with open(join(dirname(sublime.packages_path()), filepath.replace(".javatar-imports", "-converted.javatar-packages")), "w") as filew:
                filew.write(sublime.encode_value(packages_file, True))
                sublime.message_dialog("Conversion Done\nTotal Packages: " + str(total_package) + "\nTotal Classes: " + str(total_class))
