import sublime
import sublime_plugin
import os
import urllib
from ...core import (
    ActionHistory,
    BrowseDialog,
    DependencyManager,
    JavatarDict,
    JDKManager,
    Macro,
    Settings,
    StateProperty,
    ThreadProgress
)
from ...utils import (
    Downloader,
    StatusManager
)


class JavatarProjectSettingsCommand(sublime_plugin.WindowCommand):

    """
    Command to set the various settings for Javatar and projects
    """

    def run(self, action_type, **kwargs):
        self.action_type = action_type
        getattr(self, action_type)(**kwargs)

    def set_program_arguments(self):
        """
        Set the program arguments to pass to the main execution unit
        """
        arguments = Settings().get("program_arguments", "")
        panel = sublime.active_window().show_input_panel(
            "Arguments:",
            arguments,
            self.on_set_program_arguments,
            None,
            self.on_cancel_program_arguments
        )
        panel.sel().add(sublime.Region(0, panel.size()))

    def on_set_program_arguments(self, arguments):
        """
        A callback when set the program arguments

        @param arguments: arguments to be used
        """
        Settings().set("program_arguments", arguments)

        self.show_menu("project_settings")

    def on_cancel_program_arguments(self):
        """
        A callback when cancel to set the program arguments
        """
        self.show_menu("project_settings")

    def add_library_path(self, to_global):
        """
        Show a list of folder structure to select as a library path
        """
        self.from_global = to_global
        fd = BrowseDialog(
            initial_dir=os.path.dirname(
                os.path.commonprefix(StateProperty().get_project_dirs())
            ),
            path_filter=self.directory_filter,
            selector=self.dir_selector,
            on_done=self.on_select_library_path,
            on_cancel=self.on_cancel_library_path
        )
        fd.browse(prelist=self.dir_prelist)

    def remove_library_path(self, library_path, from_global=True):
        """
        Remove specified library path from the settings

        @param library_path: a library path to remove
        @param from_global: a boolean specified whether the settings will be
            remove from global settings or not
        """
        library_paths = Settings().get(
            "library_paths",
            [],
            from_global=from_global
        )

        if library_path in library_paths:
            library_paths.remove(library_path)

        Settings().set("library_paths", library_paths, to_global=from_global)
        StateProperty().refresh_library_paths()

        menu_name = "global" if from_global else "local"
        menu_name += "_library_paths"
        self.show_menu(menu_name)
        self.show_delayed_status("Library path \"%s\" has been removed" % (
            os.path.basename(library_path)
        ))

    def on_select_library_path(self, index):
        """
        A callback when select a dependency
        """
        path = index[2:-1]

        library_paths = Settings().get(
            "library_paths", [], from_global=self.from_global
        )

        library_paths += [path]

        Settings().set(
            "library_paths",
            library_paths,
            to_global=self.from_global
        )
        StateProperty().refresh_library_paths()

        menu_name = "global" if self.from_global else "local"
        menu_name += "_library_paths"

        self.show_menu(menu_name)
        self.show_delayed_status("Library path \"%s\" has been added" % (
            os.path.basename(path)
        ))

    def on_cancel_library_path(self):
        """
        A callback when cancel to select a dependency
        """
        menu_name = "global" if self.from_global else "local"
        menu_name += "_library_paths"
        self.show_menu(menu_name)

    def get_usable_source_folders(self, path, prefix=""):
        """
        Returns a list of potential source folders

        @param path: a directory path to search
        @param prefix: a path prefix to convert to relative path
        """
        folder_list = []
        for name in os.listdir(path):
            path_name = os.path.join(path, name)
            if os.path.isdir(path_name) and not name.startswith("."):
                if StateProperty().is_source_folder(path_name):
                    folder_list.append([
                        name,
                        os.path.relpath(path_name, prefix)
                    ])
                folder_list += self.get_usable_source_folders(
                    path_name,
                    prefix
                )
        return folder_list

    def add_source_folder(self):
        """
        Show a list of potential source folders to select
        """
        self.prefix = os.path.dirname(
            os.path.commonprefix(StateProperty().get_project_dirs())
        )
        self.usable_source_folders = []
        for project_folder in StateProperty().get_project_dirs():
            self.usable_source_folders.append([
                os.path.basename(project_folder),
                os.path.relpath(project_folder, self.prefix)
            ])
            self.usable_source_folders += self.get_usable_source_folders(
                project_folder,
                self.prefix
            )
        if len(self.usable_source_folders) <= 0:
            sublime.error_message("No source folder can be use")
            return
        sublime.active_window().show_quick_panel(
            self.usable_source_folders,
            self.on_source_folder_added
        )

    def remove_source_folder(self, source_folder):
        """
        Remove a specified source folder from the settings

        @param source_folder: a source_folder to remove
        """
        source_folders = Settings().get("source_folders", [])

        if source_folder in source_folders:
            source_folders.remove(source_folder)

        Settings().set("source_folders", source_folders)
        StateProperty().refresh_source_folders()

        self.show_menu("local_source_folders")
        self.show_delayed_status("Source folder \"%s\" has been removed" % (
            os.path.basename(source_folder)
        ))

    def on_source_folder_added(self, index):
        """
        A callback when select a source folder
        """
        if index >= 0:
            source_folders = Settings().get("source_folders", [])

            path = os.path.join(
                self.prefix, self.usable_source_folders[index][1]
            )
            if path not in source_folders:
                source_folders += [path]

            Settings().set("source_folders", source_folders)

        StateProperty().refresh_source_folders()
        self.show_menu("local_source_folders")
        if index >= 0:
            self.show_delayed_status("Source folder \"%s\" has been added" % (
                self.usable_source_folders[index][1]
            ))

    def jar_file_filter(self, path):
        """
        A filter for .jar files
        """
        # TODO(spywhere): Optimize this logic (if it can)
        if (os.path.basename(path).startswith(".") and
            Settings().get("show_hidden_files_and_directories", False) and
                (os.path.isdir(path) or path.endswith(".jar"))):
            return True
        return (
            not os.path.basename(path).startswith(".") and
            (os.path.isdir(path) or path.endswith(".jar"))
        )

    def directory_filter(self, path):
        """
        A filter for directories
        """
        # TODO(spywhere): Optimize this logic (if it can)
        if (os.path.basename(path).startswith(".") and
            Settings().get("show_hidden_files_and_directories", False) and
                (os.path.isdir(path) or path.endswith(".jar"))):
            return True
        return (
            not os.path.basename(path).startswith(".") and
            os.path.isdir(path)
        )

    def file_prelist(self, path):
        dir_list = []
        dir_list.append(["[Current Directory]", path])
        if os.path.dirname(path) != path:
            dir_list.append(["[Parent Folder]", os.path.dirname(path)])
        return dir_list

    def dir_selector(self, path):
        return (path.startswith("> ") and
                path.endswith(" ") and
                os.path.isdir(path[2:-1]))

    def dir_prelist(self, path):
        dir_list = []
        dir_list.append(["[Select This Directory]", "> " + path + " "])
        if os.path.dirname(path) != path:
            dir_list.append(["[Parent Folder]", os.path.dirname(path)])
        return dir_list

    def add_maven_dependency(self):
        panel = sublime.active_window().show_input_panel(
            "Maven Dependency:",
            "groupid:artifactid:version",
            self.on_select_maven_dependency,
            None,
            self.on_cancel_maven_dependency
        )
        panel.sel().add(sublime.Region(0, panel.size()))

    def on_select_maven_dependency(self, class_path):
        """
        A callback when select the Maven dependency

        @param class_path: Maven dependency class path
        """

        host = "http://search.maven.org"
        class_path = class_path.split(":")
        error_message = "Failed to retrieve dependency informations"
        try:
            if len(class_path) > 2:
                error_message = "Failed to download dependency"
                output_location = Macro().parse(Settings().get(
                    "dependencies_download_location"
                ))
                if output_location:
                    if os.path.isfile(output_location):
                        return
                    elif not os.path.isdir(output_location):
                        try:
                            os.makedirs(output_location)
                        except:
                            pass
                groupid = class_path[0].replace(".", "/")
                artifactid = class_path[1].replace(".", "/")
                version = class_path[2]
                path = [
                    groupid,
                    artifactid,
                    version,
                    "%s-%s.jar" % (artifactid, version)
                ]
                jar_url = host + "/remotecontent?filepath=%s" % ("/".join(path))
                output_file = os.path.join(
                    output_location, os.path.basename(jar_url)
                )
                download_thread = Downloader.download_file(
                    jar_url,
                    output_file,
                    on_complete=lambda status: self.on_dependency_downloaded(
                        status, output_file
                    )
                )
                ThreadProgress(
                    download_thread,
                    "Downloading Maven dependency \"%s\"" % (
                        ":".join(class_path)
                    ), (
                        "Maven dependency \"%s\" has been " % (
                            ":".join(class_path)
                        ) + "successfully downloaded"
                    )
                )
            elif len(class_path) > 1:
                groupid = class_path[0]
                artifactid = class_path[1]
                info_thread = Downloader.request(
                    host + "/solrsearch/select?q=%s&core=gav&wt=json" % (
                        urllib.request.quote(
                            "g:\"%s\" AND a:\"%s\"" % (groupid, artifactid),
                            ""
                        )
                    ), on_complete=lambda data: self.on_maven_repo_retrieved(
                        data, groupid, artifactid
                    )
                )
                ThreadProgress(
                    info_thread, "Acquiring Maven dependency versions"
                )
            elif len(class_path) > 0:
                groupid = class_path[0]
                info_thread = Downloader.request(host + "/solrsearch/select?q=%s&wt=json" % (
                    urllib.request.quote(
                        "g:\"%s\"" % (groupid),
                        ""
                    )
                ), on_complete=lambda data: self.on_maven_repo_retrieved(
                    data, groupid
                ))
                ThreadProgress(
                    info_thread, "Acquiring Maven dependency artifacts"
                )
        except Exception as e:
            ActionHistory().add_action(
                (
                    "javatar.commands.settings" +
                    ".project_settings.on_select_maven_dependency"
                ),
                error_message,
                e
            )
            self.show_delayed_status(error_message)
            self.show_menu("local_dependencies")

    def on_maven_repo_retrieved(self, data, groupid, artifactid=None):
        try:
            json = sublime.decode_value(data.decode())
        except Exception as e:
            ActionHistory().add_action(
                (
                    "javatar.commands.settings.project_settings" +
                    ".on_maven_repo_retrieved"
                ),
                "Malform dependency informations",
                e
            )
            self.show_delayed_status("Malform dependency informations")
            self.show_menu("local_dependencies")
            return
        if "response" not in json or "docs" not in json["response"]:
            self.show_delayed_status(
                "Invalid response for dependency informations"
            )
            self.show_menu("local_dependencies")
            return
        docs = json["response"]["docs"]
        if ("numFound" not in json["response"] or
                json["response"]["numFound"] == 0):
            self.show_delayed_status(
                "No dependency available for \"%s\"" % (
                    groupid + ((":" + artifactid) if artifactid else "")
                )
            )
            self.show_menu("local_dependencies")
            return
        versions = []
        artifacts = []
        for doc in docs:
            if "a" not in doc or "id" not in doc:
                continue
            if artifactid:
                versions.append([
                    doc["a"] + doc["latestVersion"]
                    if "latestVersion" in doc else doc["v"]
                    if "v" in doc else "Unknown",
                    "ID: " + doc["id"]
                ])
            else:
                artifacts.append([
                    doc["a"],
                    "Latest Version: " + doc["latestVersion"]
                    if "latestVersion" in doc else doc["v"]
                    if "v" in doc else "Unknown"
                ])
        sublime.active_window().show_quick_panel(
            versions if artifactid else artifacts,
            lambda index: self.on_select_maven_artifact_or_version(
                index, docs
            )
        )

    def on_select_maven_artifact_or_version(self, index, docs):
        if index < 0:
            self.show_menu("local_dependencies")
            return

        self.on_select_maven_dependency(docs[index]["id"])

    def on_dependency_downloaded(self, status, path):
        if not status:
            self.show_delayed_status("Failed to download dependency \"%s\"" % (
                os.path.basename(path)
            ))
            self.show_menu("local_dependencies")
            return

        dependencies = Settings().get(
            "dependencies", [], from_global=False
        )

        if path not in dependencies:
            dependencies += [path]

        Settings().set(
            "dependencies",
            dependencies,
            to_global=False
        )
        DependencyManager().refresh_dependencies()

        self.show_delayed_status("Dependency \"%s\" has been added" % (
            os.path.basename(path)
        ))
        self.show_menu("local_dependencies")

    def on_cancel_maven_dependency(self):
        """
        A callback when cancel the Maven dependency selection
        """
        self.show_menu("local_dependencies")

    def add_external_jar(self, to_global=True):
        """
        Show a file browser to user and let them select a .jar file

        @param to_global: a boolean specified whether the settings will be save
            to global settings or not
        """
        self.from_global = to_global
        fd = BrowseDialog(
            initial_dir=Macro().parse(Settings().get("dependencies_path")),
            path_filter=self.jar_file_filter,
            on_done=self.on_select_dependency,
            on_cancel=self.on_cancel_dependency
        )
        fd.browse(prelist=self.file_prelist)

    def add_class_folder(self, to_global=True):
        """
        Show a file browser to user and let them select a class folder

        @param to_global: a boolean specified whether the settings will be save
            to global settings or not
        """
        self.from_global = to_global
        fd = BrowseDialog(
            initial_dir=Macro().parse(Settings().get("dependencies_path")),
            path_filter=self.directory_filter,
            selector=self.dir_selector,
            on_done=self.on_select_dependency,
            on_cancel=self.on_cancel_dependency
        )
        fd.browse(prelist=self.dir_prelist)

    def remove_dependency(self, dependency, from_global=True):
        """
        Remove specified dependency from the settings

        @param dependency: a dependency to remove
        @param from_global: a boolean specified whether the settings will be
            remove from global settings or not
        """
        dependencies = Settings().get(
            "dependencies",
            [],
            from_global=from_global
        )

        if dependency in dependencies:
            dependencies.remove(dependency)

        Settings().set("dependencies", dependencies, to_global=from_global)
        DependencyManager().refresh_dependencies()

        menu_name = "global" if from_global else "local"
        menu_name += "_dependencies"
        self.show_menu(menu_name)
        self.show_delayed_status("Dependency \"%s\" has been removed" % (
            os.path.basename(dependency)
        ))

    def on_select_dependency(self, index):
        """
        A callback when select a dependency
        """
        if self.action_type == "add_external_jar":
            path = index
        elif self.action_type == "add_class_folder":
            path = index[2:-1]

        dependencies = Settings().get(
            "dependencies", [], from_global=self.from_global
        )

        if path not in dependencies:
            dependencies += [path]

        Settings().set(
            "dependencies",
            dependencies,
            to_global=self.from_global
        )
        Settings().set(
            "dependencies_path",
            os.path.dirname(path),
            to_global=self.from_global
        )
        DependencyManager().refresh_dependencies()

        menu_name = "global" if self.from_global else "local"
        menu_name += "_dependencies"

        self.show_menu(menu_name)
        self.show_delayed_status("Dependency \"%s\" has been added" % (
            os.path.basename(path)
        ))

    def on_cancel_dependency(self):
        """
        A callback when cancel to select a dependency
        """
        menu_name = "global" if self.from_global else "local"
        menu_name += "_dependencies"
        self.show_menu(menu_name)

    def set_jdk(self, to_global=True):
        """
        Show a list of available JDKs to use

        @param to_global: a boolean specified whether the settings will be save
            to global settings or not
        """
        self.from_global = to_global
        JDKManager().detect_jdk(
            silent=True,
            on_done=self.on_jdk_detected,
            progress=True
        )

    def on_jdk_detected(self):
        """
        A callback when JDKs are detected
        """
        if self.from_global:
            jdks = JavatarDict(Settings().get_global("jdk_version"))
        else:
            jdks = JavatarDict(
                Settings().get_global("jdk_version"),
                Settings().get_local("jdk_version")
            )

        self.panel_list = []
        self.jdk_list = []
        default_java = JDKManager().get_jdk_version()
        if default_java:
            self.panel_list.append([
                "Default JDK",
                "Default JDK [%s]" % (
                    JDKManager().to_readable_version(
                        default_java
                    )
                )
            ])
            self.jdk_list.append("")
        if jdks.get_dict():
            for jdk in jdks.get_dict():
                if jdk == "use":
                    continue
                self.panel_list.append([
                    jdk,
                    JDKManager().to_readable_version(jdks.get(jdk))
                ])
                self.jdk_list.append(jdk)
        if len(self.jdk_list) > 0:
            sublime.active_window().show_quick_panel(
                self.panel_list,
                self.on_select_jdk
            )
        else:
            sublime.error_message(
                "Javatar cannot find JDK installed on your computer." +
                "\n\nPlease install or settings the location of installed" +
                " JDK."
            )

    def on_select_jdk(self, index):
        """
        A callback when select a JDK to use
        """
        if index >= 0:
            jdks = Settings().get("jdk_version", from_global=self.from_global)
            jdks = jdks or {}

            jdks["use"] = self.jdk_list[index]

            Settings().set("jdk_version", jdks, self.from_global)

        menu_name = "global" if self.from_global else "project"
        menu_name += "_settings"
        self.show_menu(menu_name)
        if index >= 0:
            self.show_delayed_status("%s has been set %s" % (
                self.panel_list[index][0],
                "as default" if self.from_global else "for project"
            ))
            JDKManager().detect_jdk(silent=True)

    def show_menu(self, menu_name):
        """
        Show a specified menu

        @param menu_name: a menu to show
        """
        sublime.set_timeout(
            lambda: sublime.active_window().run_command(
                "javatar", {"action": {"name": menu_name}}
            ),
            10
        )

    def show_delayed_status(self, message):
        """
        Show a message after a few delay

        @param message: a status message
        """
        sublime.set_timeout(lambda: StatusManager().show_status(message), 500)
