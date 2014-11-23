class ActionList:
    actions = []

    def add_action(self, name, action):
        from .javatar_utils import is_ready, get_settings
        if is_ready() and get_settings("enable_actions_history"):
            self.actions.append([name, action])
        elif not is_ready():
            self.actions.append([name, action])

    def is_starts_with(self, key, list):
        for e in list:
            if key.startswith(e):
                return True
        return False

    def get_action(self, include=None, exclude=None):
        """
        This method returns the contained actions filtered on certain
        conditions.

        @param include: if provided, filters the contained actions, including \
        them if they start with any of the provided strings
        @param exclude: if provided, filters the contained actions, excluding \
        them if they start with any of the provided strings

        @return: a list of valid actions as per arguments

        The contained actions are in the form;
        .. code-block::

            [
                ('module', 'message')
            ]

        where module is something like `javatar.utils.javatar_shell`
        this allows the user to filter by the module they wish to see
        messages from

        """
        include = include or []
        exclude = exclude or []

        return [
            action[1]
            for action in self.actions
            if (
                (len(include) <= 0 or self.is_starts_with(action[0], include)) and
                (len(exclude) <= 0 or not self.is_starts_with(action[0], exclude))
            )
        ]

    def clear_action(self):
        self.actions = {}


ACTION = None


def get_action():
    global ACTION
    if ACTION is None:
        ACTION = ActionList()
    return ACTION


def add_action(name, action):
    get_action().add_action(name, action)
