import sublime
import os
from .action_history import ActionHistory
from .helper_service import HelperService
from .java_utils import JavaClassPath, JavaUtils
from .state_property import StateProperty
from .settings import Settings
from ..parser.GrammarParser import GrammarParser


class _JavaStructure:
    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def file_with_class_path(self, class_path):
        class_path = JavaClassPath(class_path)
        jpackage = class_path.get_package()
        jclass = class_path.get_class()

        path_list = StateProperty().get_source_folders()
        output_path = None
        while len(jpackage) > 0:
            for path in path_list:
                if os.path.exists(path, jpackage[0]):
                    output_path = os.path.join(path, jpackage[0])
                    path_list = os.listdir(output_path)
                    jpackage = jpackage[1:]
                    continue
            output_path = None
            break
        if not output_path:
            return None
        for file_name in os.listdir(output_path):
            file_path = os.path.join(output_path, file_name)
            if jclass.get() in self.classes_in_java_file(file_path):
                return file_path
        return None

    def find_class_paths_for_classes(self, classes, include_local=True,
                                     custom_filter=None, callback=None):
        from ..threads import BackgroundThread
        if callback:
            return BackgroundThread(
                func=self.find_class_paths_for_classes,
                args=[classes, include_local, custom_filter],
                on_complete=callback
            )
        class_paths = {}
        found_classes = []
        if include_local:
            for source_folder in StateProperty().get_source_folders():
                for root, dir_names, file_names in os.walk(source_folder):
                    for file_name in file_names:
                        for class_name in classes:
                            if file_name != class_name + ".java":
                                continue
                            class_path = ".".join([
                                x for x in [
                                    JavaUtils().to_package(
                                        root
                                    ).as_class_path(),
                                    class_name
                                ] if x
                            ])
                            if class_name in class_paths:
                                class_paths[class_name].append(class_path)
                            else:
                                class_paths[class_name] = [class_path]
                            if class_name not in found_classes:
                                found_classes.append(class_name)

        cont = True
        if custom_filter:
            cont, cl_paths = custom_filter()
            for class_name in cl_paths:
                if class_name in class_paths:
                    class_paths[class_name] += cl_paths[class_name]
                else:
                    class_paths[class_name] = cl_paths[class_name]
        if cont:
            cl_paths = HelperService().get_class_paths_for_classes(classes)
            for class_name in cl_paths:
                if class_name in class_paths:
                    class_paths[class_name] += cl_paths[class_name]
                else:
                    class_paths[class_name] = cl_paths[class_name]
        for class_name in class_paths:
            class_paths[class_name].sort()
        return class_paths

    def package_declarations_in_file(self, file_path):
        if not JavaUtils().is_java_file(file_path):
            return []
        try:
            parser = GrammarParser(sublime.decode_value(sublime.load_resource(
                "Packages/Javatar/grammars/Java8.javatar-grammar"
            )))

            java_file = open(file_path, "r")
            source_code = java_file.read()
            java_file.close()
            parse_output = parser.parse_grammar(source_code)
            if parse_output["success"]:
                return parser.find_by_selectors(
                    Settings().get("package_declaration_selector")
                )
        except Exception as e:
            ActionHistory().add_action(
                "javatar.core.java_structure.classes_in_file",
                "Error while parsing",
                e
            )
        return None

    def imports_and_types_in_file(self, file_path):
        if not JavaUtils().is_java_file(file_path):
            return []
        imports_and_types = {
            "imports": [],
            "import_nodes": [],
            "types": []
        }
        try:
            parser = GrammarParser(sublime.decode_value(sublime.load_resource(
                "Packages/Javatar/grammars/Java8.javatar-grammar"
            )))

            java_file = open(file_path, "r")
            source_code = java_file.read()
            java_file.close()
            parse_output = parser.parse_grammar(source_code)
            if parse_output["success"]:
                type_declarations = parser.find_by_selectors(
                    Settings().get("type_selectors")
                )
                for type_declaration in type_declarations:
                    imports_and_types["types"].append(
                        type_declaration["value"]
                    )

                declarations = parser.find_by_selectors(
                    Settings().get("declarations_selector")
                )
                imports_and_types["import_nodes"] = parser.find_by_selectors(
                    Settings().get("import_declaration_selector"),
                    declarations
                )
                import_declarations = parser.find_by_selectors(
                    Settings().get("import_declaration_package_selector"),
                    declarations
                )
                for import_declaration in import_declarations:
                    class_path = JavaClassPath(import_declaration["value"])
                    imports_and_types["imports"].append(
                        class_path
                    )
        except Exception as e:
            ActionHistory().add_action(
                "javatar.core.java_structure.classes_in_file",
                "Error while parsing",
                e
            )
        return imports_and_types

    def classes_in_file(self, file_path):
        if not JavaUtils().is_java_file(file_path):
            return []
        classes = []
        try:
            parser = GrammarParser(sublime.decode_value(sublime.load_resource(
                "Packages/Javatar/grammars/Java8.javatar-grammar"
            )))

            java_file = open(file_path, "r")
            source_code = java_file.read()
            java_file.close()
            parse_output = parser.parse_grammar(source_code)
            if parse_output["success"]:
                class_names = parser.find_by_selectors(
                    Settings().get("class_declaration_name_selector"),
                )
                for class_name in class_names:
                    nodes = parser.find_by_selectors(
                        Settings().get("class_members_filter_selector") % (
                            class_name["value"]
                        )
                    )
                    classes.append({
                        "name": class_name["value"],
                        "nodes": nodes
                    })
        except Exception as e:
            ActionHistory().add_action(
                "javatar.core.java_structure.classes_in_file",
                "Error while parsing",
                e
            )

        return classes

    def constructors_in_class(self, jclass):
        constructors = []

        ctors = GrammarParser.filter_by_selectors(
            Settings().get("class_constructors_selector"),
            jclass["nodes"]
        )

        for ctor in ctors:
            ctor_child = GrammarParser.filter_inside_region(
                [ctor["begin"], ctor["end"]],
                jclass["nodes"]
            )
            ctor_name = GrammarParser.filter_by_selectors(
                Settings().get("class_constructor_name_selector"),
                ctor_child
            )
            if ctor_name:
                params = []

                param_list = GrammarParser.filter_by_selectors(
                    Settings().get("parameter_selector"),
                    ctor_child
                )

                for param in param_list:
                    param_child = GrammarParser.filter_inside_region(
                        [param["begin"], param["end"]],
                        ctor_child
                    )
                    param_type = GrammarParser.filter_by_selectors(
                        Settings().get("parameter_type_selector"),
                        param_child
                    )
                    param_name = GrammarParser.filter_by_selectors(
                        Settings().get("parameter_name_selector"),
                        param_child
                    )
                    if param_type and param_name:
                        params.append({
                            "type": param_type[0]["value"],
                            "name": param_name[0]["value"]
                        })

                constructors.append({
                    "name": ctor_name[0]["value"],
                    "params": params
                })

        return constructors

    def fields_in_class(self, jclass):
        field_list = []

        fields = GrammarParser.filter_by_selectors(
            Settings().get("class_fields_selector"),
            jclass["nodes"]
        )

        for field in fields:
            field_child = GrammarParser.filter_inside_region(
                [field["begin"], field["end"]],
                jclass["nodes"]
            )
            field_type = GrammarParser.filter_by_selectors(
                Settings().get("class_field_type_selector"),
                field_child
            )
            field_name = GrammarParser.filter_by_selectors(
                Settings().get("class_field_name_selector"),
                field_child
            )
            if field_type and field_name:
                field_list.append({
                    "type": field_type[0]["value"],
                    "name": field_name[0]["value"]
                })

        return field_list

    def methods_in_class(self, jclass):
        method_list = []

        methods = GrammarParser.filter_by_selectors(
            Settings().get("class_methods_selector"),
            jclass["nodes"]
        )

        for method in methods:
            method_child = GrammarParser.filter_inside_region(
                [method["begin"], method["end"]],
                jclass["nodes"]
            )
            method_return_type = GrammarParser.filter_by_selectors(
                Settings().get("class_method_type_selector"),
                method_child
            ) or [{"value": "void"}]
            method_name = GrammarParser.filter_by_selectors(
                Settings().get("class_method_name_selector"),
                method_child
            )
            if method_return_type and method_name:
                params = []

                param_list = GrammarParser.filter_by_selectors(
                    Settings().get("parameter_selector"),
                    method_child
                )

                for param in param_list:
                    param_child = GrammarParser.filter_inside_region(
                        [param["begin"], param["end"]],
                        method_child
                    )
                    param_type = GrammarParser.filter_by_selectors(
                        Settings().get("parameter_type_selector"),
                        param_child
                    )
                    param_name = GrammarParser.filter_by_selectors(
                        Settings().get("parameter_name_selector"),
                        param_child
                    )
                    if param_type and param_name:
                        params.append({
                            "type": param_type[0]["value"],
                            "name": param_name[0]["value"]
                        })

                method_list.append({
                    "name": method_name[0]["value"],
                    "returnType": method_return_type[0]["value"],
                    "params": params
                })

        return method_list


def JavaStructure():
    return _JavaStructure.instance()
