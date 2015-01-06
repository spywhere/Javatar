import sublime
import threading
from os.path import basename
from .action_history import ActionHistory
from .thread_progress import ThreadProgress
from ..parser.GrammarParser import GrammarParser


class SnippetsManager:

    """
    Load and store all snippets
    """

    @staticmethod
    def reset():
        """
        Resets all stored data
        """
        ActionHistory.add_action(
            "javatar.core.snippets_manager.reset", "Reset all snippets"
        )
        SnippetsManager.snippets = None

    @staticmethod
    def on_snippets_loaded(snippets):
        """
        Callback after snippets are loaded

        @param snippets: snippets list
        """
        SnippetsManager.snippets = snippets

    @staticmethod
    def startup(on_done=None):
        """
        Loads snippets

        @param on_done: callback after loaded
        """
        SnippetsManager.load_snippets(on_done=on_done)

    @staticmethod
    def load_snippets(on_done=None):
        """
        Loads snippets

        @param on_done: callback after loaded
        """
        ActionHistory.add_action(
            "javatar.core.snippets_manager.startup", "Load snippets"
        )
        thread = SnippetsManagerThread(SnippetsManager.on_snippets_loaded)
        ThreadProgress(
            thread, "Loading Javatar snippets",
            "Javatar snippets has been successfully loaded",
            on_done=on_done
        )

    @staticmethod
    def ready():
        """
        Returns whether manager ready to be used
        """
        return SnippetsManager.snippets is not None


class SnippetsManagerThread(threading.Thread):
    def __init__(self, on_complete=None):
        self.running = True
        self.on_complete = on_complete
        self.parser = GrammarParser(sublime.decode_value(sublime.load_resource(
            "Packages/Javatar/grammars/JavatarSnippet.javatar-grammar"
        )))
        threading.Thread.__init__(self)

    def analyse_snippet(self, filename):
        """
        Analyse snippet source and returns snippet informations

        @param filename: path to snippet file
        """
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
                        "javatar.core.snippets_manager_thread.analyse_snippet",
                        "Snippet has no title [file=" + filename + "]"
                    )
                    return None
                dest = self.parser.find_by_selectors("@DescriptionValue")
                if dest:
                    snippet["description"] = dest[0]["value"]
                else:
                    ActionHistory.add_action(
                        "javatar.core.snippets_manager_thread.analyse_snippet",
                        "Snippet has no description [file=" + filename + "]"
                    )
                    return None
                data = self.parser.find_by_selectors("@DataValue")
                if data:
                    snippet["data"] = data[0]["value"]
                else:
                    ActionHistory.add_action(
                        "javatar.core.snippets_manager_thread.analyse_snippet",
                        "Snippet has no data [file=" + filename + "]"
                    )
                    return None
                return snippet
        except Exception as e:
            ActionHistory.add_action(
                "javatar.core.snippets_manager_thread.analyse_snippet",
                "Error occurred while parsing snippet [file=" + filename + "]",
                e
            )
        return None

    def run(self):
        """
        Search for all snippets and load them
        """
        snippets = []

        for filepath in sublime.find_resources("*.javatar-snippet"):
            ActionHistory.add_action(
                "javatar.core.snippets_manager_thread.analyse_snippet",
                "Analyse snippet [file=" + filepath + "]"
            )
            snippet = self.analyse_snippet(filepath)
            if snippet:
                ActionHistory.add_action(
                    "javatar.core.snippets_manager_thread.load_status",
                    "Javatar snippet " + snippet["title"] + " loaded [file=" +
                    filepath + "]"
                )
                print("[Javatar] Snippet " + basename(filepath) + " loaded")
                snippets.append(snippet)
            else:
                ActionHistory.add_action(
                    "javatar.core.snippets_manager_thread.load_status",
                    "Javatar snippet load failed [file=" + filepath + "]"
                )

        self.running = False
        self.result = True
        if self.on_complete is not None:
            sublime.set_timeout(lambda: self.on_complete(snippets), 10)
