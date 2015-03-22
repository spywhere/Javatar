from copy import deepcopy


class JavatarDict:

    """
    A custom key-value dictionary which merged two dictionaries as one
        and will always return a value no matter is there a specified
        key or not

    Local dictionary always has higher priority than global dictionary
    """

    def __init__(self, global_dict=None, local_dict=None):
        self.global_dict = global_dict or {}
        self.local_dict = local_dict or {}

    def get_dict(self, customMerger=None):
        """
        Returns a merged dictionary to be used

        @param customMerger: if provided, both dictionaries will be passed to
            that merger
        """
        global_dict = deepcopy(self.global_dict)
        if customMerger is not None:
            return customMerger(global_dict, self.local_dict)
        for key in self.local_dict:
            global_dict[key] = self.local_dict[key]
        return global_dict

    def has(self, key, in_global=True, in_local=True):
        """
        Returns whether specified key is exists or not

        @param key: a key to check
        @param in_global: if provided as True, will check against global
            dictionary
        @param in_local: if provided as True, will check against local
            dictionary
        """
        return (in_global and
                key in self.global_dict
                ) or (in_local and
                      key in self.local_dict)

    def get(self, key, default=None):
        """
        Returns a value in dictionary (if any)
            otherwise, return a default value

        @param key: a key to get value
        @param default: a return value when specified key is not exists

        This method must returns in local-global-default prioritize order
        """
        if self.has(key, in_global=False, in_local=True):
            return self.local_dict[key]
        elif self.has(key, in_global=True, in_local=False):
            return self.global_dict[key]
        else:
            return default

    def set(self, key, val, to_global=False):
        """
        Set a value to specified key in dictionary

        @param key: a key to set value
        @param val: a value to be set, if provided as not None,
            otherwise key will be deleted instead
        @param to_global: if provided as True, will set the value to
            global dictionary
        """
        if val is None:
            if self.has(key, in_global=False, in_local=True):
                del self.local_dict[key]
            elif self.has(key, in_global=True, in_local=False):
                del self.global_dict[key]
        else:
            if to_global:
                self.global_dict[key] = val
            else:
                self.local_dict[key] = val

    def get_local_dict(self):
        """
        Returns a local dictionary
        """
        return self.local_dict

    def get_global_dict(self):
        """
        Returns a global dictionary
        """
        return self.global_dict
