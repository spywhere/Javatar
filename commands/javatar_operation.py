import sublime
import sublime_plugin
from Javatar.utils import *


class JavatarOperationCommand(sublime_plugin.TextCommand):
    operation_list = [["Correct Class", "Correct package and class name in current file"], ["Rename Class", "Rename current class"], ["Rename Package", "Rename current package"]]

    def run(self, edit, type=""):
        if type == "correct_class":
            if isFile() and isJava():
                classRegion = self.view.find(getSettings("class_name_prefix")+getSettings("class_name_scope")+getSettings("class_name_suffix"), 0)
                classCode = self.view.substr(classRegion)
                classPrefix = re.search(getSettings("class_name_prefix"), classCode, re.I | re.M).group(0)
                classSuffix = re.search(getSettings("class_name_suffix"), classCode, re.I | re.M).group(0)
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
        elif type == "rename_class":
            if isFile() and isJava():
                classRegion = self.view.find(getSettings("class_name_prefix")+getSettings("class_name_scope")+getSettings("class_name_suffix"), 0)
                classCode = self.view.substr(classRegion)
                classCode = re.sub(getSettings("class_name_prefix"), "", classCode)
                classCode = re.sub(getSettings("class_name_suffix"), "", classCode)
                # sublime.message_dialog("Class: " + classCode)
                sublime.message_dialog("Work in progress...\nPlease check back later...")
            else:
                if not isFile():
                    sublime.error_message("Cannot specify package path because file is not store on the disk")
                elif not isJava():
                    sublime.error_message("Current file is not Java")
        elif type == "rename_package":
            packageRegion = self.view.find(getSettings("package_name_prefix")+getSettings("package_name_scope")+getSettings("package_name_suffix"), 0)
            packageCode = self.view.substr(packageRegion)
            packageCode = re.sub(getSettings("package_name_prefix"), "", packageCode)
            packageCode = re.sub(getSettings("package_name_suffix"), "", packageCode)
            # sublime.message_dialog("Package: " + packageCode)
            sublime.message_dialog("Work in progress...\nPlease check back later...")
        else:
            self.view.window().show_quick_panel(self.operation_list, self.type)

    def type(self, index=-1):
        if index == 0:
            self.view.run_command("javatar_operation", {"type": "correct_class"})
        elif index == 1:
            self.view.run_command("javatar_operation", {"type": "rename_class"})
        elif index == 2:
            self.view.run_command("javatar_operation", {"type": "rename_package"})
