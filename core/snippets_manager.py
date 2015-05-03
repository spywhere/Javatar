from .action_history import ActionHistory
from .thread_progress import ThreadProgress
from ..threads import SnippetsLoaderThread


class _SnippetsManager:

    """
    Load and store all snippets
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.reset(silent=True)

    def reset(self, silent=False):
        """
        Resets all stored data
        """
        if not silent:
            ActionHistory().add_action(
                "javatar.core.snippets_manager.reset", "Reset all snippets"
            )
        self.snippets = None

    def on_snippets_loaded(self, snippets):
        """
        Callback after snippets are loaded

        @param snippets: snippets list
        """
        self.snippets = snippets

    def startup(self, on_done=None):
        """
        Loads snippets

        @param on_done: callback after loaded
        """
        self.load_snippets(on_done=on_done)

    def load_snippets(self, on_done=None):
        """
        Loads snippets

        @param on_done: callback after loaded
        """
        ActionHistory().add_action(
            "javatar.core.snippets_manager.startup", "Load snippets"
        )
        thread = SnippetsLoaderThread(self.on_snippets_loaded)
        ThreadProgress(
            thread, "Loading Javatar snippets",
            "Javatar snippets has been successfully loaded",
            on_done=on_done
        )

    def get_snippet(self, title=None):
        """
        Returns a specified snippet, if found
            otherwise, return None

        @param title: a snipet title
        """
        for snippet in self.snippets:
            if snippet["title"] == title:
                return snippet
        return None

    def get_snippet_info_list(self):
        """
        Returns snippet informations as a list
        """
        snippets = []
        for snippet in self.snippets:
            snippets.append([snippet["title"], snippet["description"]])
        return snippets

    def ready(self):
        """
        Returns whether manager ready to be used
        """
        return self.snippets is not None


def SnippetsManager():
    return _SnippetsManager.instance()
