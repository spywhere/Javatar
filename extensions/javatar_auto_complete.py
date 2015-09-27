# import sublime
from ..core import EventHandler
from Javatar.api import *


class JavatarAutoComplete(JavatarPlugin):
    def debug_only(self):
        return True

    def on_load(self):
        EventHandler().register_handler(
            lambda view=None, key=None, operator=None, operand=None, match_all=None:
            self.on_query_context(self, view, key, operator, operand, match_all),
            EventHandler().ON_QUERY_CONTEXT
        )
        EventHandler().register_handler(
            lambda view=None, prefix=None, locations=None:
            self.on_query_completions(self, view, prefix, locations),
            EventHandler().ON_QUERY_COMPLETIONS
        )

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "javatar.auto_complete.trigger":
            # sublime.set_timeout(lambda: view.run_command(
            #     "auto_complete", {"key": "javatar.auto_complete.complete"}
            # ), 5000)
            return False
        elif key == "javatar.auto_complete.complete":
            return True

    def on_query_completions(self, view, prefix, locations):
        return []
        # return ([
        #     ("Oh\tString", "Oh"), ("Wow\tvoid", "Wow"), ("Okay\tfloat", "Okay")
        # ], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
