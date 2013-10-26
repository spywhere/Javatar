# QuickMenu Example
# Type 'QuickMenu' in command pallete to see some possible commands
#
# QuickMenu Example by: spywhere
# Please give credit to me!


from QuickMenu.QuickMenu import *
import sublime_plugin

# Using it within WindowCommand or any command type you want
class QuickMenuCommand(sublime_plugin.WindowCommand):
	# A variable to store a QuickMenu instance
	qm = None
	# An example menu
	menu = {
		# Startup menu
		"main": {
			# Its items
			"items": [["Dialogs...", "All dialog items"], ["Items...", "Do action on item"], ["Commands...", "Run command"]],
			# Item's actions
			"actions": [
			{
				# Redirect to "dialogs" submenu
				"name": "dialogs"
			}, {
				# Redirect to "items" submenu
				"name": "items"
			}, {
				# Redirect to "commands" submenu
				"name": "commands"
			}
			]
		},
		# Custom menu named "dialogs"
		"dialogs": {
			# Selected second item as default
			"selected_index": 2,
			"items": [["Back", "Back to previous menu"], ["Message Dialog", "Hello, World on Message Dialog"], ["Error Dialog", "Hello, World on Error Dialog"]],
			"actions": [
			{
				"name": "main",
			}, {
				# This will select "Message Dialog command" on "commands" menu
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
				# Show a message dialog
				"command": "message_dialog",
				"args": "Message: Hello, World"
			}, {
				# Show an error dialog
				"command": "error_dialog",
				"args": "Error: Hello, World"
			}, {
				# Run custom command
				"command": "open_file",
				"args": {
					"file": "${packages}/User/Preferences.sublime-settings"
				}
			}
			]
		}
	}

	# This method receive a passing menu and action which can be use like this in keymap or other part of your package
	#
	# "command": "quick_menu",
	# "args": {
	# 	"action": {
	# 		"name": "main"
	# 	}
	# }
	#
	# or custom menu on the go!
	#
	# "command": "quick_menu",
	# "args": {
	# 	"menu": {
	# 		"main": {
	# 			//Blah Blah
	# 		}
	# 	}
	# }
	#
	def run(self, menu=None, action=None):
		# If QuickMenu is not instantiated yet
		if self.qm is None:
			# If passing menu is not None
			if menu is not None:
				# Set it
				self.menu = menu
			# Instantiate QuickMenu with menu from self.menu
			self.qm = QuickMenu(self.menu)
		# Show the menu on self.window and pass on_done to self.select with passing menu and action
		# More API documentation on README file
		self.qm.show(self.window, self.select, menu, action)

	def select(self, info):
		# if selected item's index is less than 0 (cancel menu selection)
		if info["index"] < 0:
			# Open console to see these messages (View > Show Console)
			print("Exit menu level " + str(info["level"]) + " and is from sublime: " + str(info["from_sublime"]))
		else:
			# items = menu's items <list>
			# index = item's index <int>
			# level = menu level (this is used to prevent self recursion menu) <int>
			# from_sublime = is selected item comes from menu opened by sublime? <bool>
			print("Select item \"" + str(info["items"][info["index"]]) + "\" at menu level " + str(info["level"]) + " and is from sublime: " + str(info["from_sublime"]))