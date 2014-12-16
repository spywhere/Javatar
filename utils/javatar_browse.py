import sublime
import os


class JavatarBrowseDialog():
    def __init__(self, initial_dir, path_filter=None, selector=None, window=None, on_done=None, on_cancel=None):
        if window is None:
            self.window = sublime.active_window()
        else:
            self.window = window
        if selector is None:
            self.selector = self.default_selector
        else:
            self.selector = selector
        self.path_filter = path_filter
        self.on_done = on_done
        self.on_cancel = on_cancel
        self.initial_dir = initial_dir
        self.prelist = None
        self.postlist = None

    def default_selector(self, path):
        return os.path.isfile(path)

    def get_list(self, path):
        dir_list = []
        if self.prelist is not None:
            dir_list += self.prelist(path)
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if not name.startswith(".") and os.path.isdir(pathname) and (self.path_filter is None or self.path_filter is not None and self.path_filter(pathname)):
                dir_list.append(["[" + name + "]", pathname])
        for name in os.listdir(path):
            pathname = os.path.join(path, name)
            if not name.startswith(".") and os.path.isfile(pathname) and (self.path_filter is None or self.path_filter is not None and self.path_filter(pathname)):
                dir_list.append([name, pathname])
        if self.postlist is not None:
            dir_list += self.postlist(path)
        return dir_list

    def browse(self, current_dir=None, prelist=None, postlist=None):
        if current_dir is None:
            current_dir = self.initial_dir
        if prelist is not None and self.prelist is None:
            self.prelist = prelist
        if postlist is not None and self.postlist is None:
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
