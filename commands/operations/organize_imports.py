import sublime
import sublime_plugin
import re
from ...core import (
    ActionHistory,
    HelperService,
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

    def not_in_imports(self, class_name, class_paths):
        for class_path in class_paths:
            if class_path.get_class().get() == class_name:
                return False
        return True

    def run(self, edit):
        if not StateProperty().is_java():
            sublime.error_message("Current file is not Java")
        BackgroundThread(
            func=self.organize_step_one,
            args=[],
            on_complete=self.organize_step_two
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
            unimport = (
                self.not_in_imports(
                    class_name, imports_and_types["imports"]
                ) and class_name not in self.unimportTypes
            )
            if unimport:
                self.unimportTypes.append(class_name)
        self.organize_step_two()

    def organize_step_two(self, index=0):
        if index == 0:
            ActionHistory().add_action(
                (
                    "javatar.commands.operations" +
                    ".organize_imports.organize_step_two"
                ),
                "Organize Imports Step 2 - Find unimport classes"
            )
        if len(self.unimportTypes) > 0 and index < len(self.unimportTypes):
            JavaStructure().find_class_paths_for_class(
                self.unimportTypes[index],
                callback=lambda cps: self.organize_step_two_callback(
                    index, cps
                )
            )
            StatusManager().show_status(
                "Searching package for type \"%s\" %.2f%%..." % (
                    self.unimportTypes[index],
                    index * 100 / len(self.unimportTypes)
                ),
                delay=-1,
                ref="organize_imports"
            )
        else:
            self.organize_step_four()

    def organize_step_two_callback(self, index, class_paths):
        StatusManager().hide_status("organize_imports")
        if class_paths:
            self.select_class_path(index, class_paths)
        elif self.unimportTypes[index] not in self.missingTypes:
            self.missingTypes.append(
                self.unimportTypes[index]
            )
            self.organize_step_two(index + 1)

    def organize_step_three(self, index, class_path):
        if index == 0:
            ActionHistory().add_action(
                (
                    "javatar.commands.operations" +
                    ".organize_imports.organize_step_three"
                ),
                "Organize Imports Step 3 - Class path selection"
            )
        if isinstance(class_path, int):
            if self.unimportTypes[index] not in self.userTypes:
                self.userTypes.append(self.unimportTypes[index])
        elif class_path is not None:
            self.importedTypes.append(class_path)
        if index < len(self.unimportTypes):
            self.organize_step_two(index + 1)
        else:
            self.organize_step_four()

    def organize_step_four(self):
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_four"
            ),
            "Organize Imports Step 4 - Add default imports"
        )
        JavaStructure().find_class_paths_for_class(
            "",
            False,
            self.default_package_filter,
            callback=self.organize_step_four_callback
        )
        StatusManager().show_status(
            "Searching package for default type...",
            delay=-1,
            ref="organize_imports"
        )

    def organize_step_four_callback(self, class_paths):
        StatusManager().hide_status("organize_imports")
        self.importedTypes.extend(class_paths)
        self.organize_step_five()

    def organize_step_five(self, index=0):
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_five"
            ),
            "Organize Imports Step 5 - Ask for remaining types"
        )
        if index == 0:
            self.missingTypes += self.userTypes
        if len(self.missingTypes) > 0 and index < len(self.missingTypes):
            self.ask_for_package(index, -1, self.missingTypes[index])
        else:
            self.organize_step_seven()

    def organize_step_six(self, index, class_path):
        ActionHistory().add_action(
            (
                "javatar.commands.operations" +
                ".organize_imports.organize_step_six"
            ),
            "Organize Imports Step 6 - User packages selection"
        )
        if class_path:
            self.importedTypes.append(class_path)
        if index < len(self.missingTypes):
            self.organize_step_five(index + 1)
        else:
            self.organize_step_seven()

    def organize_step_seven(self):
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
            "Organize Imports Step 6 - Organize the imports"
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

    def default_package_filter(self):
        class_paths = []
        missing = []
        while len(self.missingTypes) > 0:
            paths = HelperService().get_class_paths_for_class(
                self.missingTypes[0]
            )
            if len(paths) <= 0:
                missing.append(self.missingTypes[0])
                self.missingTypes.remove(self.missingTypes[0])
                continue
            self.missingTypes.remove(self.missingTypes[0])
            path = paths[0]
            if path.startswith("java.lang."):
                continue
            if path not in (class_paths + self.importedTypes):
                class_paths.append(path)
        self.missingTypes = missing
        return False, class_paths

    def select_class_path(self, unimport_index, class_paths, index=None):
        class_paths = class_paths or []
        manual_enter_text = "Enter Package Manually"
        if index is None:
            if len(class_paths) > 1:
                class_paths.append(manual_enter_text)
                sublime.set_timeout(
                    self.view.window().show_quick_panel(
                        class_paths,
                        lambda i: self.select_class_path(
                            unimport_index, class_paths, i
                        )
                    ),
                    10
                )
            else:
                self.organize_step_three(
                    unimport_index,
                    class_paths[0] if len(class_paths) > 0 else None
                )
        elif index < 0:
            self.organize_step_three(unimport_index, None)
        elif class_paths[index] == manual_enter_text:
            ActionHistory().add_action(
                (
                    "javatar.commands.operations" +
                    ".organize_imports.select_class_path"
                ),
                "Organize Imports - Enter Package Manually"
            )
            self.organize_step_three(unimport_index, -1)
        else:
            self.organize_step_three(unimport_index, class_paths[index])

    def ask_for_package(self, index, package=None, class_name="",
                        default_value=""):
        StatusManager().hide_status("ask_package_description")
        class_path = ".".join([str(x) for x in [package, class_name] if x])
        if not package:
            self.organize_step_six(index, None)
        elif isinstance(package, int):
            sublime.set_timeout(
                lambda: self.view.window().show_input_panel(
                    "Package for class \"%s\":" % (class_name),
                    default_value,
                    lambda pkg: self.ask_for_package(
                        index, pkg, class_name
                    ),
                    lambda pkg: self.ask_description(pkg, class_name),
                    lambda: self.ask_for_package(
                        index, None, class_name
                    )
                ),
                10
            )
        elif JavaUtils().is_class_path(class_path):
            self.organize_step_six(index, class_path)
        else:
            sublime.error_message("Invalid package naming")
            self.ask_for_package(index, -1, class_name, package)

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

    def description(self):
        return "Organize Imports"
