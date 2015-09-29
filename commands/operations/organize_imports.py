import sublime
import sublime_plugin
import re
from ...core import (
    ActionHistory,
    JavaStructure,
    JavaClassPath,
    JavaUtils,
    StateProperty
)
from ...threads import BackgroundThread
from ...utils import StatusManager


class JavatarOrganizeImports(sublime_plugin.TextCommand):
    def reset(self):
        self.useTypes = []
        self.importedTypes = []
        self.unimportTypes = []
        self.missingTypes = []
        self.userTypes = []

    def class_path_for_type(self, class_name, class_paths):
        for class_path in class_paths:
            if class_path.get_class().get() == class_name:
                return class_path
        return None

    def run(self, edit):
        if not StateProperty().is_java():
            sublime.error_message("Current file is not Java")
        BackgroundThread(
            func=self.organize_step_one,
            args=[],
            on_complete=lambda x: self.organize_step_two()
        )
        StatusManager().show_status(
            "Gathering class informations...",
            delay=-1,
            ref="organize_imports"
        )

    def organize_step_one(self):
        self.reset()
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_one"
            ),
            "Organize Imports Step 1 - Gathering imported types and use types"
        )
        imports_and_types = JavaStructure().imports_and_types_in_file(
            self.view.file_name()
        )
        self.import_nodes = imports_and_types["import_nodes"]

        for class_name in imports_and_types["types"]:
            self.useTypes.append(class_name)
            class_path = self.class_path_for_type(
                class_name, imports_and_types["imports"]
            )
            unimport = (
                not class_path and class_name not in self.unimportTypes
            )
            if unimport:
                self.unimportTypes.append(class_name)
            elif (class_path and
                    class_path.as_class_path() not in self.importedTypes):
                self.importedTypes.append(class_path.as_class_path())

    def organize_step_two(self):
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_two"
            ),
            "Organize Imports Step 2 - Find unimport types"
        )

        if len(self.unimportTypes) > 0:
            JavaStructure().find_class_paths_for_classes(
                self.unimportTypes,
                callback=self.organize_step_two_callback
            )
            StatusManager().show_status(
                "Searching packages for missing types...",
                delay=-1,
                ref="organize_imports"
            )
        else:
            self.organize_step_four()

    def organize_step_two_callback(self, class_paths):
        StatusManager().hide_status("organize_imports")

        for class_name in self.unimportTypes:
            if (class_name not in class_paths.keys() and
                    class_name not in self.missingTypes):
                self.missingTypes.append(class_name)
        self.organize_step_three(class_paths)

    def organize_step_three(self, class_paths):
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_three"
            ),
            "Organize Imports Step 3 - Class path selections (%s left)" % (
                len(class_paths)
            )
        )
        if len(class_paths) > 0:
            class_name, cl_paths = class_paths.popitem()
            self.select_class_paths(class_paths, class_name, cl_paths)
        else:
            self.organize_step_four()

    def organize_step_three_callback(self, remains, class_name, class_path):
        if isinstance(class_path, int):
            if class_name not in self.userTypes:
                self.userTypes.append(class_name)
        elif class_path is not None and class_path not in self.importedTypes:
            self.importedTypes.append(class_path)
        if len(remains) > 0:
            self.organize_step_three(remains)
        else:
            self.organize_step_four()

    def select_class_paths(self, remains, class_name, class_paths, index=None):
        class_paths = class_paths or []
        manual_enter_text = "Enter Package Manually"
        if index is None:
            if len(class_paths) > 1:
                class_paths.append(manual_enter_text)
                sublime.set_timeout(
                    self.view.window().show_quick_panel(
                        class_paths,
                        lambda i: self.select_class_paths(
                            remains, class_name, class_paths, i
                        )
                    ),
                    10
                )
            else:
                self.organize_step_three_callback(
                    remains, class_name,
                    class_paths[0] if class_paths else None
                )
        elif index < 0:
            self.organize_step_three_callback(
                remains, class_name, None
            )
        elif class_paths[index] == manual_enter_text:
            self.organize_step_three_callback(
                remains, class_name, -1
            )
        else:
            self.organize_step_three_callback(
                remains, class_name, class_paths[index]
            )

    def organize_step_four(self):
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_four"
            ),
            "Organize Imports Step 4 - Ask for remaining types (%s left)" % (
                len(self.missingTypes + self.userTypes)
            )
        )
        self.missingTypes += self.userTypes
        self.userTypes = []
        if len(self.missingTypes) > 0:
            self.ask_for_package(self.missingTypes.pop(), -1)
        else:
            self.organize_step_five()

    def ask_for_package(self, class_name, package=None, default_value=""):
        StatusManager().hide_status("ask_package_description")
        class_path = ".".join([str(x) for x in [package, class_name] if x])
        if not package:
            self.organize_step_four()
        elif isinstance(package, int):
            sublime.set_timeout(
                lambda: self.view.window().show_input_panel(
                    "Package for class \"%s\":" % (class_name),
                    default_value,
                    lambda pkg: self.ask_for_package(
                        class_name, pkg
                    ),
                    lambda pkg: self.ask_description(pkg, class_name),
                    lambda: self.ask_for_package(
                        class_name, None
                    )
                ),
                10
            )
        elif JavaUtils().is_class_path(class_path):
            if class_path and class_path not in self.importedTypes:
                self.importedTypes.append(class_path)
            self.organize_step_four()
        else:
            sublime.error_message("Invalid package naming")
            self.ask_for_package(class_name, -1, package)

    def ask_description(self, package, class_name):
        status = "Class \"%s\" will use \"%s\" package to organize import" % (
            class_name, package
        )
        class_path = ".".join([x for x in [package, class_name] if x])
        if not JavaUtils().is_class_path(class_path):
            status = "Invalid package naming"
        StatusManager().show_status(
            status,
            delay=-1,
            ref="ask_package_description"
        )

    def organize_step_five(self):
        StatusManager().show_status(
            "Organizing imports...",
            delay=-1,
            ref="organize_imports"
        )
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_six"
            ),
            "Organize Imports Step 5 - Organize the imports"
        )
        current_package = JavaUtils().to_package(StateProperty().get_dir())
        import_code = ""
        if not current_package.is_empty():
            import_code += "package " + current_package.as_class_path() + ";"
        import_code += "\n\n"

        package_declarations = JavaStructure().package_declarations_in_file(
            self.view.file_name()
        )
        import_start = 0
        import_end = 0
        if len(package_declarations) > 0:
            import_start = package_declarations[0]["begin"]
            import_end = package_declarations[-1]["end"]
        if len(self.import_nodes) > 0:
            import_end = self.import_nodes[-1]["end"]

        while re.search(
                "\\s", self.view.substr(sublime.Region(
                    import_end, import_end+1
                ))):
            import_end += 1

        imported_classes = []
        for class_path in self.importedTypes:
            cl_path = JavaClassPath(class_path)
            cl_package = cl_path.get_package().as_class_path()
            local_package = current_package.as_class_path()
            if (class_path.startswith("java.lang.") or
                    cl_package == local_package):
                continue
            if (cl_path.get_class().get() in self.useTypes and
                    not cl_path.get_package().is_empty()):
                imported_classes.append(class_path)

        imported_classes.sort()
        first = True
        for class_path in imported_classes:
            if not first:
                import_code += "\n"
            import_code += "import %s;" % (class_path)
            first = False

        if import_code:
            import_code += "\n\n"
            self.view.run_command("javatar_utils", {
                "util_type": "replace",
                "region": [import_start, import_end],
                "text": import_code,
                "dest": "Organize Imports"
            })
        StatusManager().hide_status("organize_imports")
        sublime.set_timeout(lambda: StatusManager().show_status(
            "Imports has been organized"
        ), 500)

    def description(self):
        return "Organize Imports"
