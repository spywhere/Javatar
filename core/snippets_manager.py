from .action_history import ActionHistory
from .thread_progress import ThreadProgress
from ..threads import SnippetsLoaderThread


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
        thread = SnippetsLoaderThread(SnippetsManager.on_snippets_loaded)
        ThreadProgress(
            thread, "Loading Javatar snippets",
            "Javatar snippets has been successfully loaded",
            on_done=on_done
        )

    @staticmethod
    def get_snippet(title=None):
        """
        Returns a specified snippet, if found
            otherwise, return None

        @param title: a snipet title
        """
        for snippet in SnippetsManager.snippets:
            if snippet["title"] == title:
                return snippet
        return None

    @staticmethod
    def get_snippet_info_list():
        """
        Returns snippet informations as a list
        """
        snippets = []
        for snippet in SnippetsManager.snippets:
            snippets.append([snippet["title"], snippet["description"]])
        return snippets

    @staticmethod
    def ready():
        """
        Returns whether manager ready to be used
        """
        return SnippetsManager.snippets is not None
