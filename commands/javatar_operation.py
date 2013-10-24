import sublime
import sublime_plugin
import re
from Javatar.utils import *


class JavatarCorrectClassCommand(sublime_plugin.TextCommand):
    def run(self, edit, type="", text=""):
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


class JavatarOrganizeImportsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        classList = set()
        # From variables
        variableClassRegions = self.view.find_all(getSettings("class_match"))
        for reg in variableClassRegions:
            classList.add(self.view.substr(reg))

        # From static class
        staticClassRegion = self.view.find_all(getSettings("static_class_match"))
        for reg in staticClassRegion:
            classList.add(self.view.substr(reg))

        # From base type
        baseTypeRegion = self.view.find_all(getSettings("base_type_match"))
        for reg in baseTypeRegion:
            classList.add(self.view.substr(reg))

        # From import
        importPackageRegion = self.view.find_all(getSettings("import_match"))
        for imreg in importPackageRegion:
            packageClass = re.search(getSettings("package_class_match"), self.view.substr(imreg), re.M).group(0)
            classList.discard(packageClass)

        # Package element
        packageElementRegion = self.view.find_all(getSettings("package_element_match"))
        for reg in packageElementRegion:
            classList.discard(self.view.substr(reg))

        # Variables name
        variableRegion = self.view.find_all(getSettings("variable_match"))
        for reg in variableRegion:
            classList.discard(self.view.substr(reg))

        # Classes in current package
        samePackageClass = list(classList)
        for sClass in samePackageClass:
            if getPath("exist", getPath("join", getPath("current_dir"), sClass+".java")):
                classList.discard(sClass)


        classList = list(classList)


        self.view.window().show_quick_panel(classList, self.organizeClass)

        # A = Class list from variable
        # B = Class list from static class
        # C = Base type
        # D = Class list from import (find import then find class)
        # E = Package element
        # F = All classes with package
        # X = (A+B+C)-(D+E+F) = Class need to import

        # If import conflict
        # conflictClass = ["me.spywhere.package.Class", "Class.java"], ["me.spywhere.Class", "Class.java"]
        # self.view.window().show_quick_panel(conflictClass, self.organizeClass)

    def organizeClass(self, index=-1):
        pass


class JavatarRenameOperationCommand(sublime_plugin.WindowCommand):
    def run(self, text="", type=""):
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
