import sublime
import sublime_plugin
import re
from os.path import join, exists
from ..utils import (
    is_file,
    add_action,
    get_class,
    is_java,
    get_current_package,
    get_settings,
    get_class_name,
    is_debug,
    get_package_path,
    find_class,
    get_class_name_by_regex,
    get_packages,
    show_status,
    get_package_root_dir,
    get_all_types,
    is_package,
    to_package,
    get_current_dir
)


class JavatarTestOperationCommand(sublime_plugin.WindowCommand):
    def run(self, class_name=None):
        if class_name is None:
            self.window.show_input_panel("Class Name:", "", self.run, None, None)
        else:
            get_class(class_name, self.window, self.class_callback)

    def class_callback(self, class_info, local):
        print("Local: " + str(local))
        print(str(class_info))


class JavatarCorrectClassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        add_action(
            "javatar.command.operation.correct_class.run", "Correct class"
        )
        if is_file() and is_java():
            packageName = get_current_package()
            packageRegions = self.view.find_by_selector(get_settings("package_name_selector"))
            classRegions = self.view.find_by_selector(get_settings("class_name_selector"))
            if len(classRegions) > 0:
                self.view.replace(edit, classRegions[0], get_class_name(self.view.file_name()))
            if packageName != "":
                if len(packageRegions) > 0:
                    self.view.replace(edit, packageRegions[0], packageName)
                else:
                    self.view.insert(edit, 0, "package " + packageName + ";\n")
        else:
            if not is_file():
                sublime.error_message("Cannot specify package path because file is not store on the disk")
            elif not is_java():
                sublime.error_message("Current file is not Java")

    def description(self):
        return "Correct Class"


class JavatarOrganizeImportsCommand(sublime_plugin.TextCommand):
    # import annotation
    # import classes, generic classes
    # import interfaces, superclasses
    #
    # if test on Bukkit Plugin passed then it should work perfectly
    #
    # TODO:
    #     Performance!
    #     Option to create a new class or enter it manually when no class is found

    classes = []
    ctype = None
    selectedPackage = None
    importedPackages = []
    importedPackagesStat = {}
    alwaysImportedPackages = []
    importedTypes = []
    useTypes = []
    needImportTypes = []
    askTypes = []
    postAskTypes = []
    index = 0

    def reset(self):
        self.classes = []
        self.ctype = None
        self.selectedPackage = None
        self.importedPackages = []
        self.importedPackagesStat = {}
        self.alwaysImportedPackages = []
        self.importedTypes = []
        self.useTypes = []
        self.needImportTypes = []
        self.askTypes = []
        self.postAskTypes = []
        self.index = 0

    def getClasses(self, textScope):
        classes = []
        genericClass = re.search(".*(?=<.*>)", textScope)
        if genericClass is not None:
            classes.append(genericClass.group(0))
            insideClasses = re.search("(?<=<).*(?=>)", textScope)
            if insideClasses is not None:
                for clazz in re.sub("\\s+", "", insideClasses.group(0)).split(","):
                    classes += self.getClasses(clazz)
        else:
            arrayClass = re.search(".*(?=\\[.*\\])", textScope)
            if arrayClass is not None:
                classes.append(arrayClass.group(0))
            else:
                if textScope.startswith("@"):
                    classes.append(textScope[1:])
                else:
                    classes.append(textScope)
        return classes

    def organize_step_zero(self, edit):
        # gathering info
        self.reset()
        add_action("javatar.command.operation.organize_imports.step0", "Organize Imports [step=0] Gathering info")
        importedPackagesRegions = self.view.find_by_selector(get_settings("package_import_selector"))
        useTypesRegions = self.view.find_by_selector(get_settings("type_selector"))

        primitiveTypes = get_settings("primitive_type")

        for region in useTypesRegions:
            if self.view.substr(region) not in primitiveTypes:
                self.useTypes += self.getClasses(self.view.substr(region))
            elif is_debug():
                print("useType: " + self.view.substr(region))

        for region in importedPackagesRegions:
            package = self.view.substr(region)
            self.importedPackages.append(package)
            self.importedTypes.append(get_class_name(self.view.substr(region)))
            if get_package_path(package) in self.importedPackagesStat:
                self.importedPackagesStat[get_package_path(package)] += 1
            else:
                self.importedPackagesStat[get_package_path(package)] = 1

        for useType in self.useTypes:
            if useType not in self.importedTypes and useType not in self.needImportTypes and (not is_file() or (is_file() and not exists(join(get_current_dir(), useType + ".java")))):
                self.needImportTypes.append(useType)

        self.index = 0
        self.run(edit, 1)

    def organize_step_one(self, edit):
        # select classes
        add_action("javatar.command.operation.organize_imports.step1", "Organize Imports [step=1] Select classes")
        if len(self.needImportTypes) > 0 and self.index < len(self.needImportTypes):
            classes = find_class(get_package_root_dir(), self.needImportTypes[self.index])
            if len(classes) > 0:
                self.selectClasses(None, classes)
            else:
                if self.needImportTypes[self.index] not in self.askTypes:
                    self.askTypes.append(self.needImportTypes[self.index])
                self.index += 1
                self.run(edit, 1)
        else:
            self.index = 0
            self.run(edit, 3)

    def organize_step_two(self, edit):
        # select classes callback
        add_action(
            "javatar.command.operation.organize_imports.step2",
            "Organize Imports [step=2] Select classes callback"
        )
        if isinstance(self.selectedPackage, int):
            if self.needImportTypes[self.index] not in self.postAskTypes:
                self.postAskTypes.append(self.needImportTypes[self.index])
        else:
            if self.selectedPackage is not None:
                if get_package_path(self.selectedPackage) in self.importedPackagesStat:
                    self.importedPackagesStat[get_package_path(self.selectedPackage)] += 1
                else:
                    self.importedPackagesStat[get_package_path(self.selectedPackage)] = 1
                self.importedPackages.append(self.selectedPackage)
                self.importedTypes.append(self.needImportTypes[self.index])
        self.index += 1
        if self.index >= len(self.needImportTypes):
            self.index = 0
            self.run(edit, 3)
        else:
            self.run(edit, 1)

    def organize_step_three(self, edit):
        # add default imports
        add_action(
            "javatar.command.operation.organize_imports.step3",
            "Organize Imports [step=3] Add default imports"
        )
        for packageImport in get_packages():
            importOnce = False
            if "packages" in packageImport:
                for packageName in packageImport["packages"]:
                    package = packageImport["packages"][packageName]
                    for importType in get_all_types(package):
                        if importType in self.askTypes:
                            importOnce = True
                            self.askTypes.remove(importType)
                            if "default" in package and package["default"]:
                                continue
                            packageCode = packageName + "." + importType
                            if packageCode not in self.importedPackages:
                                self.importedPackages.append(packageCode)
                            if packageCode in self.importedPackagesStat:
                                self.importedPackagesStat[packageCode] += 1
                            else:
                                self.importedPackagesStat[packageCode] = 1
                    if not importOnce and "always_import" in packageImport and packageImport["always_import"]:
                        self.alwaysImportedPackages.append(packageName)
        self.run(edit, 4)

    def organize_step_four(self, edit):
        # ask package
        add_action(
            "javatar.command.operation.organize_imports.step4",
            "Organize Imports [step=4] Ask package"
        )
        self.askTypes += self.postAskTypes
        if len(self.askTypes) > 0 and self.index < len(self.askTypes):
            self.askPackage(-1, self.askTypes[self.index])
        else:
            self.run(edit, 6)

    def organize_step_five(self, edit):
        # ask package callback
        add_action(
            "javatar.command.operation.organize_imports.step5",
            "Organize Imports [step=5] Ask package callback"
        )
        if self.selectedPackage is not None:
            self.importedPackages.append(self.selectedPackage)
            if get_package_path(self.selectedPackage) in self.importedPackagesStat:
                self.importedPackagesStat[get_package_path(self.selectedPackage)] += 1
            else:
                self.importedPackagesStat[get_package_path(self.selectedPackage)] = 1
        self.index += 1
        if self.index >= len(self.askTypes):
            self.index = 0
            self.run(edit, 6)
        else:
            self.run(edit, 4)

    def organize_step_six(self, edit):
        # import
        add_action(
            "javatar.command.operation.organize_imports.step6",
            "Organize Imports [step=6] Import"
        )
        importCode = ""

        #clear old imports
        packageRegions = self.view.find_by_selector(get_settings("package_meta_selector"))
        if len(packageRegions) > 0:
            importCode += self.view.substr(packageRegions[0]) + "\n\n"
            self.view.replace(edit, packageRegions[0], "")
        else:
            importCode += "\n\n"

        importsRegions = self.view.find_by_selector(get_settings("import_meta_selector"))
        while len(importsRegions) > 0:
            regionWithNewLine = sublime.Region(importsRegions[0].begin(), importsRegions[0].end() + 1)
            while self.view.substr(regionWithNewLine)[-1] == "\n":
                regionWithNewLine = sublime.Region(regionWithNewLine.begin(), regionWithNewLine.end() + 1)
            regionWithNewLine = sublime.Region(regionWithNewLine.begin(), regionWithNewLine.end() - 1)
            self.view.replace(edit, regionWithNewLine, "")
            importsRegions = self.view.find_by_selector(get_settings("import_meta_selector"))

        importedPackages = []

        for alwaysImportPackage in self.alwaysImportedPackages:
            for importPackage in self.importedPackages:
                if importPackage.startswith(alwaysImportPackage):
                    self.importedPackages.remove(importPackage)

        for importPackage in self.importedPackages:
            if get_class_name_by_regex(importPackage) in self.useTypes:
                importedPackages.append(importPackage)
        for importPackage in self.alwaysImportedPackages:
            importedPackages.append(importPackage + ".*")

        if is_debug():
            print(str(self.importedPackagesStat))
        importedPackages.sort()

        for importPackage in importedPackages:
            importCode += "import " + importPackage + ";\n"

        if importCode != "":
            importCode += "\n"
            #Remove whitespace at start of file
            while re.search("\\s+$", self.view.substr(sublime.Region(0, 1))) is not None:
                self.view.replace(edit, sublime.Region(0, 1), "")
            self.view.run_command("javatar_util", {"util_type": "insert", "text": importCode, "dest": "Organize Imports"})
            if get_class_name() is None:
                className = "<Unknown>"
            else:
                className = get_class_name()
            sublime.set_timeout(lambda: show_status("Imports organized in class \"" + className + "\""), 500)

    def run(self, edit, step=0):
        if step == 0:
            self.organize_step_zero(edit)

        elif step == 1:
            self.organize_step_one(edit)

        elif step == 2:
            self.organize_step_two(edit)

        elif step == 3:
            self.organize_step_three(edit)

        elif step == 4:
            self.organize_step_four(edit)

        elif step == 5:
            self.organize_step_five(edit)

        elif step == 6:
            self.organize_step_six(edit)

    def selectClasses(self, index=None, classes=[]):
        if index is None:
            self.classes = classes
            if len(classes) > 1:
                classes.append("Enter Package Manually")
                sublime.set_timeout(lambda: self.view.window().show_quick_panel(classes, self.selectClasses), 10)
            elif len(classes) == 1:
                self.selectedPackage = classes[0]
                self.view.run_command("javatar_organize_imports", {"step": 2})
            else:
                self.selectedPackage = None
                self.view.run_command("javatar_organize_imports", {"step": 2})
        else:
            if index < 0:
                self.selectedPackage = None
            else:
                if self.classes[index] == "Enter Package Manually":
                    add_action(
                        "javatar.command.operation.organize_imports.step2",
                        "Organize Imports - Enter Package Manually"
                    )
                    self.selectedPackage = -1
                else:
                    self.selectedPackage = self.classes[index]
            self.view.run_command("javatar_organize_imports", {"step": 2})

    def askPackage(self, package=None, ctype=""):
        if package is None:
            self.selectedPackage = None
            self.view.run_command("javatar_organize_imports", {"step": 5})
        elif isinstance(package, int):
            self.ctype = ctype
            sublime.set_timeout(lambda: self.view.window().show_input_panel("Package for type \"" + ctype + "\":", "", self.askPackage, "", self.askPackage), 10)
        else:
            if is_package(package):
                self.selectedPackage = package + "." + self.ctype
                self.view.run_command("javatar_organize_imports", {"step": 5})
            elif package == "":
                self.selectedPackage = None
                self.view.run_command("javatar_organize_imports", {"step": 5})
            else:
                sublime.message_dialog("Invalid package naming")
                self.askPackage(-1, self.ctype)

    def description(self):
        return "Organize Imports"


class JavatarRenameOperationCommand(sublime_plugin.WindowCommand):
    def run(self, text="", rename_type=""):
        add_action(
            "javatar.command.operation.rename.run",
            "Rename [rename_type={}]"
            .format(rename_type)
        )
        if rename_type == "class":
            if is_file() and is_java():
                classRegion = sublime.active_window().active_view().find(get_settings("class_name_prefix") + get_settings("class_name_scope") + get_settings("class_name_suffix"), 0)
                classCode = sublime.active_window().active_view().substr(classRegion)
                classCode = re.sub(get_settings("class_name_prefix"), "", classCode)
                classCode = re.sub(get_settings("class_name_suffix"), "", classCode)
                if text is None or text == "":
                    sublime.active_window().show_input_panel("New Class Name:", classCode, self.run, "", "")
                sublime.message_dialog("Work in progress...\nPlease check back later...")
            else:
                if not is_file():
                    sublime.error_message("Cannot specify package path because file is not store on the disk")
                elif not is_java():
                    sublime.error_message("Current file is not Java")
        elif rename_type == "package":
            currentPackage = to_package(get_current_dir())
            if text is None or text == "":
                sublime.active_window().show_input_panel("New Package Name:", currentPackage, self.run, "", "")
