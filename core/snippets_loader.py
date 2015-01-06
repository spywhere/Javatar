import sublime
import re
import threading
from .action_history import ActionHistory
from .thread_progress import ThreadProgress
from ..parser.GrammarParser import GrammarParser


class SnippetsLoader:

    """
    Load and store all snippets
    """

    @staticmethod
    def reset():
        ActionHistory.add_action(
            "javatar.core.snippets_loader.reset", "Reset all snippets"
        )
        SnippetsLoader.snippets = None

    @staticmethod
    def on_snippets_loaded(snippets):
        SnippetsLoader.snippets = snippets

    @staticmethod
    def startup():
        ActionHistory.add_action(
            "javatar.core.snippets_loader.startup", "Load snippets"
        )
        thread = SnippetsLoaderThread(SnippetsLoader.on_snippets_loaded)
        thread.start()
        ThreadProgress(
            thread, "Loading Javatar snippets",
            "Javatar snippets has been loaded"
        )

    @staticmethod
    def ready():
        return SnippetsLoader.snippets is not None


class SnippetsLoaderThread(threading.Thread):
    def __init__(self, on_complete=None):
        self.on_complete = on_complete
        self.parser = GrammarParser(sublime.decode_value(sublime.load_resource(
            "Packages/Javatar/grammars/JavatarSnippet.javatar-grammar"
        )))
        threading.Thread.__init__(self)

    def analyse_snippet(self, filename):
        data = sublime.load_resource(filename)

        try:
            parse_output = self.parser.parse_grammar(data)

            if parse_output["success"] and parse_output["end"] == len(data):
                snippet = {"file": filename}
                title = self.parser.find_by_selectors("@TitleValue")
                if title:
                    snippet["title"] = title[0]["value"]
                else:
                    ActionHistory.add_action(
                        "javatar.core.snippets_loader_thread.analyse_snippet",
                        "Snippet has no title [file=" + filename + "]"
                    )
                    return None
                dest = self.parser.find_by_selectors("@DescriptionValue")
                if dest:
                    snippet["description"] = dest[0]["value"]
                else:
                    ActionHistory.add_action(
                        "javatar.core.snippets_loader_thread.analyse_snippet",
                        "Snippet has no description [file=" + filename + "]"
                    )
                    return None
                data = self.parser.find_by_selectors("@DataValue")
                if data:
                    snippet["data"] = data[0]["value"]
                else:
                    ActionHistory.add_action(
                        "javatar.core.snippets_loader_thread.analyse_snippet",
                        "Snippet has no data [file=" + filename + "]"
                    )
                    return None
                return snippet
        except Exception as e:
            ActionHistory.add_action(
                "javatar.core.snippets_loader_thread.analyse_snippet",
                "Error occurred while parsing snippet [file=" + filename + "]",
                e
            )
        return None

    def run(self):
        snippets = []

        for filepath in sublime.find_resources("*.javatar-snippet"):
            ActionHistory.add_action(
                "javatar.core.snippets_loader_thread.analyse_snippet",
                "Analyse snippet [file=" + filepath + "]"
            )
            print("[Javatar] Loading snippet " + filepath)
            snippet = self.analyse_snippet(filepath)
            if snippet:
                ActionHistory.add_action(
                    "javatar.core.snippets_loader_thread.load_status",
                    "Javatar snippet " + snippet["title"] + " loaded [file=" +
                    filepath + "]"
                )
                print("[Javatar] Snippet " + snippet["title"] + " loaded")
            else:
                ActionHistory.add_action(
                    "javatar.core.snippets_loader_thread.load_status",
                    "Javatar snippet load failed [file=" + filepath + "]"
                )
            snippets.append(snippet)

        self.result = True
        if self.on_complete is not None:
            sublime.set_timeout(lambda: self.on_complete(snippets), 10)
