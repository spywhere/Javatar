import copy
import sublime


class QuickMenu:
	settings = {
		"menu": [],
		"max_level": 50,
		"silent": False
	}
	tmp = {
		"menu": None,
		"select": None,
		"window": None,
		"callback": None,
		"sublime": True,
		"level": 0
	}

	def __init__(self, menu=[], silent=False, max_level=50):
		self.settings["menu"] = copy.deepcopy(menu)
		self.settings["max_level"] = max_level
		self.settings["silent"] = silent

	def set(self, item, value):
		self.settings[item] = value

	def setMenu(self, name, menu):
		self.settings["menu"][name] = copy.deepcopy(menu)

	def setItems(self, menu, items, actions):
		if menu in self.settings["menu"] and "items" in self.settings["menu"][menu] and "actions" in self.settings["menu"][menu]:
			self.settings["menu"][menu]["items"] = copy.deepcopy(items)
			self.settings["menu"][menu]["actions"] = copy.deepcopy(actions)

	def addItems(self, menu, items, actions):
		if menu in self.settings["menu"] and "items" in self.settings["menu"][menu] and "actions" in self.settings["menu"][menu]:
			self.settings["menu"][menu]["items"] += copy.deepcopy(items)
			self.settings["menu"][menu]["actions"] += copy.deepcopy(actions)

	def show(self, window=None, on_done=None, menu=None, select=None, flags=0, on_highlight=None, level=0):
		selected_index = -1
		if window is None and self.tmp["window"] is not None:
			window = self.tmp["window"]
			self.tmp["window"] = None
		if window is None and not self.settings["silent"]:
			sublime.message_dialog("No window to show")
			return
		if on_done is None and self.tmp["callback"] is not None:
			on_done = self.tmp["callback"]
		if self.settings["menu"] is None or "main" not in self.settings["menu"] or "items" not in self.settings["menu"]["main"]:
			if not self.settings["silent"]:
				sublime.message_dialog("No menu to show")
			return
		if menu is None and self.tmp["menu"] is not None:
			menu = self.tmp["menu"]
			self.tmp["menu"] = None
		if menu is None or "items" not in menu:
			menu = self.settings["menu"]["main"]
		if select is None and self.tmp["select"] is not None:
			select = self.tmp["select"]
			self.tmp["select"] = None
		if select is not None:
			if "name" in select:
				if select["name"] not in self.settings["menu"]:
					if not self.settings["silent"]:
							sublime.message_dialog("No menu found")
					return
				menu = self.settings["menu"][select["name"]]
				if "item" in select and "actions" in menu:
					if level >= self.settings["max_level"]:
						if not self.settings["silent"]:
							sublime.message_dialog("Seem like menu go into too many levels now...")
						return
					if len(menu["actions"]) < select["item"]:
						if not self.settings["silent"]:
							sublime.message_dialog("Invalid menu selection")
						return
					self.tmp["sublime"] = False
					self.show(window, on_done, menu, menu["actions"][select["item"]-1], flags, on_highlight, level+1)
					return
			elif "command" in select:
				if "args" in select:
					if select["command"] == "message_dialog":
						sublime.message_dialog(select["args"])
					elif select["command"] == "error_dialog":
						sublime.error_message(select["args"])
					else:
						sublime.active_window().run_command(select["command"], select["args"])
				else:
					sublime.active_window().run_command(select["command"])
				return
			elif not self.settings["silent"]:
				sublime.message_dialog("No action assigned")
				return
			else:
				return
		if "selected_index" in menu:
			selected_index = menu["selected_index"]-1
		self.tmp["menu"] = menu
		self.tmp["window"] = window
		self.tmp["callback"] = on_done
		self.tmp["level"] = self.tmp["level"]+1
		window.show_quick_panel(menu["items"], self.select, flags, selected_index, on_highlight)

	def select(self, index=-1):
		if self.tmp["callback"] is not None:
			self.tmp["callback"]({"index": index, "level": self.tmp["level"], "from_sublime": self.tmp["sublime"]})
		if index < 0:
			self.tmp["menu"] = None
			self.tmp["select"] = None
			self.tmp["window"] = None
			self.tmp["callback"] = None
			self.tmp["sublime"] = True
			self.tmp["level"] = 0
			return
		if "actions" in self.tmp["menu"] and len(self.tmp["menu"]["actions"]) > index:
			self.tmp["select"] = self.tmp["menu"]["actions"][index]
			self.tmp["sublime"] = False
			sublime.set_timeout(self.show, 50)