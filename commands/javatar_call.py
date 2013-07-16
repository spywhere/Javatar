import sublime_plugin


class JavatarCallCommand(sublime_plugin.TextCommand):
    def run(self, edit, type=""):
        sels = self.view.sel()
        for sel in sels:
            if type == "package_name":
                self.view.insert(edit, sel.a, "Package.Subpackage")
            elif type == "subpackage_name":
                self.view.insert(edit, sel.a, "MyPackage")
            elif type == "full_class_name":
                self.view.insert(edit, sel.a, "Package.Class")
            elif type == "class_name":
                self.view.insert(edit, sel.a, "MyClass")
            else:
                self.view.insert(edit, sel.a, "Javatar Call")
        # Show command dialog for returning a package name or anything related
