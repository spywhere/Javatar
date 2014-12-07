import sublime_plugin


class JavatarViewCommand(sublime_plugin.WindowCommand):
    def run(self):
        group, index = self.window.get_view_index(self.window.active_view())
        if index < 0:
            print("Current view group is %s" % (group))
        else:
            print("Current view index is %s" % (index))
            print("Current view group is %s" % (group))
