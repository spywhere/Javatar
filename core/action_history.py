from .settings import Settings


class ActionHistory:

    """
    Store logs and exceptions occurred while running

    This will be useful when solving the issue
    """

    actions = []

    @staticmethod
    def reset():
        """
        Reset all changes (used on restart)
        """
        ActionHistory.actions = []

    @staticmethod
    def add_action(name, message):
        """
        Add action to the action history except specified not to (in settings)

        @param name: an action name in following format (if possible)

            javatar.[code module].[code file].[code method].[code action]

        if a class is a command, code method will be the command name instead

        @param message: an action summary that is short but clear

        """
        if not Settings.ready() or Settings.get("enable_action_history"):
            ActionHistory.actions.append((name, message))

    @staticmethod
    def is_starts_with(string, values):
        """
        Returns whether string starts with one of value in value list

        @param string: a string to check against list of value
        @param values: a list of value to check

        """
        for e in values:
            if string.startswith(e):
                return True
        return False

    @staticmethod
    def get_action(include=None, exclude=None):
        """
        Returns a list of actions filtered by specified inclusions or exclusions

        @param include: if provided, will use to filter the actions by
            including them if they starts with any of the provided strings
        @param exclude: if provided, will use to filter the actions by
            excluding them if they starts with any of the provided strings

        """

        include = include or ()
        exclude = exclude or ()
        return [
            action[1]
            for action in ActionHistory.actions
            if (
                (len(include) <= 0 or
                 ActionHistory.is_starts_with(action[0], include))
                and
                (len(include) <= 0 or
                 not ActionHistory.is_starts_with(action[0], exclude))
            )
        ]
