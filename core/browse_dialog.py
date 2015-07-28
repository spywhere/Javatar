import sublime
import os


class BrowseDialog:

    """
    A file browser with filters and selectors supported
    """

    def __init__(self, initial_dir, path_filter=None, selector=None,
                 window=None, on_done=None, on_cancel=None):
        self.window = window or sublime.active_window()
        self.selector = selector or self.default_selector
        self.path_filter = path_filter or self.default_path_filter
        self.on_done = on_done
        self.on_cancel = on_cancel
        self.initial_dir = initial_dir
        self.prelist = self.default_prelist
        self.postlist = self.default_postlist

    def default_path_filter(self, pathname):
        return True

    def default_prelist(self, path):
        return []

    def default_postlist(self, path):
        return []

    def default_selector(self, path):
        return os.path.isfile(path)

    def get_list(self, path):
        dir_list = []
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if self.path_filter(pathname):
                if os.path.isdir(pathname):
                    dir_list.append(["[" + name + "]", pathname])
                elif os.path.isfile(pathname):
                    dir_list.append([name, pathname])
        return self.prelist(path) + dir_list + self.postlist(path)

    def browse(self, current_dir=None, prelist=None, postlist=None):
        if current_dir is None:
            current_dir = self.initial_dir
        if prelist:
            self.prelist = prelist
        if postlist:
            self.postlist = postlist
        self.dir_list = self.get_list(current_dir)
        selected = 0
        if len(self.dir_list) > 1:
            selected = 1
        self.window.show_quick_panel(self.dir_list, self.on_select, 0, selected)

    def on_select(self, index):
        if index < 0:
            if self.on_cancel is not None:
                self.on_cancel()
            return
        path = self.dir_list[index][1]
        if self.selector(path):
            if self.on_done is not None:
                self.on_done(path)
            return
        else:
            sublime.set_timeout(lambda: self.browse(path), 10)
