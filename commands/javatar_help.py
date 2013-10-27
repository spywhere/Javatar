import sublime
import sublime_plugin
from ..utils import *


class JavatarHelpCommand(sublime_plugin.WindowCommand):
	action = ""

	def run(self, selector=None, action=""):
		if self.action != "":
			action = self.action
			self.action = ""
		if action == "actions_history":
			if not getSettings("enable_actions_history"):
				sublime.message_dialog("Actions History is disabled. Please enable them first.")
				return
			self.action = action
			if selector is not None:
				report = "## Javatar Report\n### System Informations\n* Javatar Version: `%javatar_version%`\n* Sublime Version: `%sublime_version%`\n* Package Path: `%packages_path%`\n* Javatar Channel: `%javatar_channel%`\n* Sublime Channel: `%sublime_channel%`\n* Platform: `%platform%`\n* As Packages: `%is_package%`\n* Package Control: `%package_control%`\n* Architecture: `%arch%`\n* Javatar's Parent Folder: `%parent_folder%`\n* Is Project: `%is_project%`\n* Is File: `%is_file%`\n* Is Java: `%is_java%`\n\n### Action List\n%actions%"
				report = report.replace("%javatar_version%", getVersion())
				report = report.replace("%javatar_channel%", str.lower(getSettings("package_channel")))
				report = report.replace("%is_package%", str(getPath("exist", getPath("join", sublime.installed_packages_path(), "Javatar.sublime-package"))))
				report = report.replace("%parent_folder%", getPath("javatar_parent"))

				report = report.replace("%sublime_version%", str(sublime.version()))
				report = report.replace("%sublime_channel%", sublime.channel())
				report = report.replace("%package_control%", str(getPath("exist", getPath("join", sublime.packages_path(), "Package Control")) or getPath("exist", getPath("join", sublime.installed_packages_path(), "Package Control.sublime-package"))))
				report = report.replace("%is_project%", str(isProject()))
				report = report.replace("%is_file%", str(isFile()))
				report = report.replace("%is_java%", str(isJava()))

				report = report.replace("%packages_path%", sublime.packages_path())
				report = report.replace("%platform%", sublime.platform())
				report = report.replace("%arch%", sublime.arch())

				selectors = selector.split("|")
				if len(selectors) > 1:
					include = selectors[0].split(",")
					exclude = selectors[1].split(",")
				else:
					include = selectors[0].split(",")
					exclude = []

				actionText = ""
				actions = getAction().getAction(include, exclude)
				c = 1
				for action in actions:
					if c > 1:
						actionText += "\n"
					actionText += str(c) + ". " + action
					c += 1
				report = report.replace("%actions%", actionText)

				view = self.window.new_file()
				view.set_name("Javatar Actions History Report")
				view.set_scratch(True)
				view.run_command("javatar_util", {"type": "add", "text": report, "dest": "Actions History"})
				view.run_command("javatar_util", {"type": "set_read_only"})
			else:
				self.window.show_input_panel("Selector: ", "", self.run, "", "")
