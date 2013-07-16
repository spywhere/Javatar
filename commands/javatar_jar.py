import sublime_plugin


class JavatarCreateJarFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create JAR File")


class JavatarCreateExeJarFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Create Executable JAR File")
