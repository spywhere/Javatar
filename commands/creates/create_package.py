import sublime
import sublime_plugin
import os.path
from ...core import (
    JavaPackage,
    JavaUtils,
    StateProperty
)
from ...utils import (
    ActionHistory,
    StatusManager
)


class JavatarCreatePackageCommand(sublime_plugin.WindowCommand):

    """
    Command to show menu which use to create a new Java package
    """

    def parse_create(self, text):
        """
        If success, returns package informations from input text,
            otherwise, returns a string described an error

        @param text: text to be analysed
        """
        relative_path = True
        if text.startswith("~"):
            text = text[1:]
            relative_path = False

        if not StateProperty().is_project() and not StateProperty().is_file():
            return "Cannot specify package location"
        if not JavaUtils().is_class_path(text):
            return "Invalid package naming"

        if relative_path and StateProperty().get_dir():
            create_directory = os.path.join(
                StateProperty().get_dir(),
                JavaPackage(text).as_path()
            )
        else:
            create_directory = os.path.join(
                StateProperty().get_source_folder(),
                JavaPackage(text).as_path()
            )

        return {
            "package": JavaUtils().to_package(create_directory),
            "directory": create_directory
        }

    def on_done(self, text=""):
        """
        Create a package with informations from the input text

        @param text: text from input panel
        """
        self.hide_status()
        info = self.parse_create(text)
        if isinstance(info, str):
            sublime.error_message(info)
            return
        ActionHistory().add_action(
            "javatar.commands.create.create_package.on_done",
            "Create [info={info}]".format_map({
                "info": info
            })
        )
        if JavaUtils().create_package_path(
                info["directory"]) != JavaUtils().CREATE_SUCCESS:
            return

        sublime.set_timeout(lambda: StatusManager().show_status(
            "Package \"{package_path}\" is created".format_map({
                "package_path": info["package"].as_class_path()
            })
        ), 500)

    def on_change(self, text=""):
        """
        Shows informations about how package get created in the status bar

        @param text: text from input panel
        """
        status = ""
        info = self.parse_create(text)
        if isinstance(info, str):
            status = info
        elif os.path.exists(info["directory"]):
            status = "Package \"{package_path}\" already exists".format_map({
                "package_path": info["package"].as_class_path()
            })
        else:
            status = "Package \"{package_path}\" will be created".format_map({
                "package_path": info["package"].as_class_path()
            })
        StatusManager().show_status(
            status,
            delay=-1,
            ref="create_description"
        )

    def hide_status(self):
        """
        Hides the text that is showed by on_change
        """
        StatusManager().hide_status("create_description")

    def run(self):
        """
        Create a specified Java package
        """
        sublime.active_window().show_input_panel(
            "Package Name:",
            "",
            self.on_done,
            self.on_change,
            self.hide_status
        )
