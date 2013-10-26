import sublime
import sublime_plugin
import re
from ..utils import *


class JavatarCorrectClassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        getAction().addAction("javatar.command.operation.correct_class", "Correct class")
        if isFile() and isJava():
            classRegion = self.view.find(getSettings("class_name_prefix")+getSettings("class_name_scope")+getSettings("class_name_suffix"), 0)
            classCode = self.view.substr(classRegion)
            classPrefix = re.search(getSettings("class_name_prefix"), classCode, re.M).group(0)
            classSuffix = re.search(getSettings("class_name_suffix"), classCode, re.M).group(0)
            classRegion = sublime.Region(classRegion.a+len(classPrefix), classRegion.b-len(classSuffix))
            packageRegion = self.view.find(getSettings("package_name_prefix")+getSettings("package_name_scope")+getSettings("package_name_suffix"), 0)
            className = getPath("name", getPath("current_file"))[:-5]
            packageName = getCurrentPackage()
            self.view.replace(edit, classRegion, className)
            if packageRegion is not None and packageRegion.a != packageRegion.b:
                self.view.replace(edit, packageRegion, "package " + packageName + ";")
            else:
                self.view.insert(edit, 0, "package " + packageName + ";\n")
        else:
            if not isFile():
                sublime.error_message("Cannot specify package path because file is not store on the disk")
            elif not isJava():
                sublime.error_message("Current file is not Java")

    def description(self):
        return "Correct Class"


class JavatarUtilCommand(sublime_plugin.TextCommand):
    def run(self, edit, type="", text="", dest=None):
        if type == "insert":
            self.view.insert(edit, self.view.size(), text)
        elif type == "set_read_only":
            self.view.set_read_only(True)

    def description(self, type="", text="", dest=None):
        return dest


class JavatarOrganizeImportsCommand(sublime_plugin.WindowCommand):
    def run(self, text=""):
        getAction().addAction("javatar.command.operation.organize_imports", "Organize imports [selector="+text+"]")
        if text == "":
            self.window.show_input_panel("Selector: ", "meta.import", self.run, "", "")
        else:
            items = []
            regions = self.window.active_view().find_by_selector(text)
            for region in regions:
                items += [[self.window.active_view().substr(region), str(region.a)+":"+str(region.b)]]
            self.window.show_quick_panel(items, self.organizeClass)

    def organizeClass(self, index=-1):
        pass

    def description(self, type="", text=""):
        return "Organize Imports"


class JavatarRenameOperationCommand(sublime_plugin.WindowCommand):
    def run(self, text="", type=""):
        getAction().addAction("javatar.command.operation.rename", "Rename [type="+str(type)+"]")
        if type == "class":
            if isFile() and isJava():
                classRegion = sublime.active_window().active_view().find(getSettings("class_name_prefix")+getSettings("class_name_scope")+getSettings("class_name_suffix"), 0)
                classCode = sublime.active_window().active_view().substr(classRegion)
                classCode = re.sub(getSettings("class_name_prefix"), "", classCode)
                classCode = re.sub(getSettings("class_name_suffix"), "", classCode)
                if text is None or text == "":
                    view = sublime.active_window().show_input_panel("New Class Name:", classCode, self.run, "", "")
                    view.set_name("JavatarRename")
                sublime.message_dialog("Work in progress...\nPlease check back later...")
            else:
                if not isFile():
                    sublime.error_message("Cannot specify package path because file is not store on the disk")
                elif not isJava():
                    sublime.error_message("Current file is not Java")
        elif type == "package":
            currentPackage = toPackage(getPath("current_dir"))
            if text is None or text == "":
                view = sublime.active_window().show_input_panel("New Package Name:", currentPackage, self.run, "", "")
                view.set_name("JavatarRename")
