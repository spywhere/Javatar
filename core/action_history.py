import traceback
from .logger import Logger
from .settings import Settings


class _ActionHistory:

    """
    Store logs and exceptions occurred while running

    This will be useful when solving the issue
    """

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.reset()

    def reset(self):
        """
        Reset all changes (used on restart)
        """
        self.actions = []

    def add_action(self, name, message, exception=None):
        """
        Add action to the action history except specified not to (in settings)

        @param name: an action name in following format (if possible)

            javatar.[code module].[code file].[code method].[code action]

        if a class is a command, code method will be the command name instead

        @param message: an action summary that is short but clear
        @param exception: a caught error exception
            if provided, this will add a traceback stack to the end of a message

        """
        if not Settings().ready() or Settings().get("enable_action_history"):
            if exception:
                message += ":\n" + traceback.format_exc()
                Logger().error(
                    "%s\n%s" % (message, traceback.format_exc())
                )
            self.actions.append((name, message))

    def is_starts_with(self, string, values):
        """
        Returns whether string starts with one of value in value list

        @param string: a string to check against list of value
        @param values: a list of value to check

        """
        for e in values:
            if string.startswith(e):
                return True
        return False

    def get_action(self, include=None, exclude=None):
        """
        Returns a list of actions filtered by specified inclusions
            or exclusions

        @param include: selectors to included
            if provided, filters the contained actions, including
                them if they start with any of the provided strings

        @param exclude: selectors to excluded
            if provided, filters the contained actions, excluding
                them if they start with any of the provided strings

        """

        include = include or ()
        exclude = exclude or ()
        return [
            action[1]
            for action in self.actions
            if (
                (
                    len(include) <= 0 or
                    self.is_starts_with(action[0], include)
                ) and (
                    len(exclude) <= 0 or
                    not self.is_starts_with(action[0], exclude)
                )
            )
        ]


def ActionHistory():
    return _ActionHistory.instance()
