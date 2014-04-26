import sublime
import os

class JavatarFileDialog():
	def __init__(self, initial_dir, startswith="", endswith="", window=None, on_done=None, on_cancel=None):
		if window is None:
			self.window = sublime.active_window()
		else:
			self.window = window
		self.startswith = startswith
		self.endswith = endswith
		self.on_done = on_done
		self.on_cancel = on_cancel
		self.initial_dir = initial_dir

	def get_list(self, path):
		dir_list = []
		dir_list.append(["[Current Directory]", path])
		if os.path.dirname(path) != path:
			dir_list.append(["[Parent Folder]", os.path.dirname(path)])
		for name in os.listdir(path):
			pathname = os.path.join(path, name)
			if not name.startswith(".") and os.path.isdir(pathname):
				dir_list.append(["["+name+"]", pathname])
		for name in os.listdir(path):
			pathname = os.path.join(path, name)
			if not name.startswith(".") and os.path.isfile(pathname) and pathname.startswith(self.startswith) and pathname.endswith(self.endswith):
				dir_list.append([name, pathname])
		return dir_list

	def browse(self, current_dir=None):
		if current_dir is None:
			current_dir = self.initial_dir
		self.dir_list = self.get_list(current_dir)
		selected = 0
		if len(self.dir_list) > 1:
			selected = 1
		self.window.show_quick_panel(self.dir_list, self.on_select, 0, selected)

	def on_select(self, index):
		if index < 0:
			if self.on_cancel is not None:
				self.on_cancel()
			return
		path = self.dir_list[index][1]
		if os.path.isfile(path):
			if self.on_done is not None:
				self.on_done(path)
			return
		else:
			sublime.set_timeout(lambda:self.browse(path), 10)
