from QuickMenu.QuickMenu import *
import sublime_plugin


class QuickMenuCommand(sublime_plugin.WindowCommand):
	qm = None
	menu = {
		"main": {
			"items": [["Dialogs...", "All dialog items"], ["Items...", "Do action on item"], ["Commands...", "Run command"]],
			"actions": [
			{
				"name": "dialogs"
			}, {
				"name": "items"
			}, {
				"name": "commands"
			}
			]
		},
		"dialogs": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Message Dialog", "Hello, World on Message Dialog"], ["Error Dialog", "Hello, World on Error Dialog"]],
			"actions": [
			{
				"name": "main",
			}, {
				"name": "commands",
				"item": 2
			}, {
				"name": "commands",
				"item": 3
			}
			]
		},
		"items": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Item 2 on Dialogs", "Select item 2 in Dialogs"], ["Item 3 on Dialogs", "Select item 3 in Dialogs"], ["Item 4 on Commands", "Select item 4 in Commands"]],
			"actions": [
			{
				"name": "main",
			}, {
				"name": "dialogs",
				"item": 2
			}, {
				"name": "dialogs",
				"item": 3
			}, {
				"name": "commands",
				"item": 4
			}
			]
		},
		"commands": {
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Message Dialog command", "Hello, World on Message Dialog"], ["Error Dialog command", "Hello, World on Error Dialog"], ["Custom command", "Open User's settings file"]],
			"actions": [
			{
				"name": "main",
			}, {
				"command": "message_dialog",
				"args": "Message: Hello, World"
			}, {
				"command": "error_dialog",
				"args": "Error: Hello, World"
			}, {
				"command": "open_file",
				"args": {"file": "${packages}/User/Preferences.sublime-settings"}
			}
			]
		}
	}

	def run(self, menu=None, select=None):
		if self.qm is None:
			if menu is not None:
				self.menu = menu
			self.qm = QuickMenu(self.menu)
		# self.qm.show(window, on_done, menu, select, flags, on_highlight)
		self.qm.show(self.window, self.select, menu, select)

	def select(self, info):
		if info["index"] < 0:
			print("Exit menu level " + str(info["level"]) + " and is from sublime: " + str(info["from_sublime"]))
		else:
			print("Select item " + str(info["index"]) + " at menu level " + str(info["level"]) + " and is from sublime: " + str(info["from_sublime"]))