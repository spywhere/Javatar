import sublime
import sublime_plugin


EVENT_HANDLER = None


class EventHandler():
	ON_NEW = 0x1
	ON_NEW_ASYNC = 0x2
	ON_CLONE = 0x4
	ON_CLONE_ASYNC = 0x8
	ON_LOAD = 0x10
	ON_LOAD_ASYNC = 0x20
	ON_PRE_CLOSE = 0x40
	ON_CLOSE = 0x80
	ON_PRE_SAVE = 0x100
	ON_PRE_SAVE_ASYNC = 0x200
	ON_POST_SAVE = 0x400
	ON_POST_SAVE_ASYNC = 0x800
	ON_MODIFIED = 0x1000
	ON_MODIFIED_ASYNC = 0x2000
	ON_SELECTION_MODIFIED = 0x4000
	ON_SELECTION_MODIFIED_ASYNC = 0x8000
	ON_ACTIVATED = 0x10000
	ON_ACTIVATED_ASYNC = 0x20000
	ON_DEACTIVATED = 0x40000
	ON_DEACTIVATED_ASYNC = 0x80000

	handlers = []

	@staticmethod
	def register_handler(handler, events=0):
		EventHandler.handlers.append([handler, events])

	@staticmethod
	def unregister_handler(handler):
		for hdr in EventHandler.handlers:
			if hdr[0] == handler:
				EventHandler.handlers.remove(hdr)
				break

	@staticmethod
	def on_new(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_NEW > 0:
				if hasattr(handler, "on_new"):
					handler.on_new(view)
				else:
					handler(view)

	@staticmethod
	def on_new_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_NEW_ASYNC > 0:
				if hasattr(handler, "on_new_async"):
					handler.on_new_async(view)
				else:
					handler(view)

	@staticmethod
	def on_clone(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_CLONE > 0:
				if hasattr(handler, "on_clone"):
					handler.on_clone(view)
				else:
					handler(view)

	@staticmethod
	def on_clone_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_CLONE_ASYNC > 0:
				if hasattr(handler, "on_clone_async"):
					handler.on_clone_async(view)
				else:
					handler(view)

	@staticmethod
	def on_load(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_LOAD > 0:
				if hasattr(handler, "on_load"):
					handler.on_load(view)
				else:
					handler(view)

	@staticmethod
	def on_load_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_LOAD_ASYNC > 0:
				if hasattr(handler, "on_load_async"):
					handler.on_load_async(view)
				else:
					handler(view)

	@staticmethod
	def on_pre_close(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_PRE_CLOSE > 0:
				if hasattr(handler, "on_pre_close"):
					handler.on_pre_close(view)
				else:
					handler(view)

	@staticmethod
	def on_close(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_CLOSE > 0:
				if hasattr(handler, "on_close"):
					handler.on_close(view)
				else:
					handler(view)

	@staticmethod
	def on_pre_save(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_PRE_SAVE > 0:
				if hasattr(handler, "on_pre_save"):
					handler.on_pre_save(view)
				else:
					handler(view)

	@staticmethod
	def on_pre_save_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_PRE_SAVE_ASYNC > 0:
				if hasattr(handler, "on_pre_save_async"):
					handler.on_pre_save_async(view)
				else:
					handler(view)

	@staticmethod
	def on_post_save(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_POST_SAVE > 0:
				if hasattr(handler, "on_post_save"):
					handler.on_post_save(view)
				else:
					handler(view)

	@staticmethod
	def on_post_save_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_POST_SAVE_ASYNC > 0:
				if hasattr(handler, "on_post_save_async"):
					handler.on_post_save_async(view)
				else:
					handler(view)

	@staticmethod
	def on_modified(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_MODIFIED > 0:
				if hasattr(handler, "on_modified"):
					handler.on_modified(view)
				else:
					handler(view)

	@staticmethod
	def on_modified_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_MODIFIED_ASYNC > 0:
				if hasattr(handler, "on_modified_async"):
					handler.on_modified_async(view)
				else:
					handler(view)

	@staticmethod
	def on_selection_modified(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_SELECTION_MODIFIED > 0:
				if hasattr(handler, "on_selection_modified"):
					handler.on_selection_modified(view)
				else:
					handler(view)

	@staticmethod
	def on_selection_modified_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_SELECTION_MODIFIED_ASYNC > 0:
				if hasattr(handler, "on_selection_modified_async"):
					handler.on_selection_modified_async(view)
				else:
					handler(view)

	@staticmethod
	def on_activated(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_ACTIVATED > 0:
				if hasattr(handler, "on_activated"):
					handler.on_activated(view)
				else:
					handler(view)

	@staticmethod
	def on_activated_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_ACTIVATED_ASYNC > 0:
				if hasattr(handler, "on_activated_async"):
					handler.on_activated_async(view)
				else:
					handler(view)

	@staticmethod
	def on_deactivated(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_DEACTIVATED > 0:
				if hasattr(handler, "on_deactivated"):
					handler.on_deactivated(view)
				else:
					handler(view)

	@staticmethod
	def on_deactivated_async(view):
		for handler, event in EventHandler.handlers:
			if event&EventHandler.ON_DEACTIVATED_ASYNC > 0:
				if hasattr(handler, "on_deactivated_async"):
					handler.on_deactivated_async(view)
				else:
					handler(view)

class EventListener(sublime_plugin.EventListener):
	def on_new(self, view):
		EventHandler.on_new(view)

	def on_new_async(self, view):
		EventHandler.on_new_async(view)

	def on_clone(self, view):
		EventHandler.on_clone(view)

	def on_clone_async(self, view):
		EventHandler.on_clone_async(view)

	def on_load(self, view):
		EventHandler.on_load(view)

	def on_load_async(self, view):
		EventHandler.on_load_async(view)

	def on_pre_close(self, view):
		EventHandler.on_pre_close(view)

	def on_close(self, view):
		EventHandler.on_close(view)

	def on_pre_save(self, view):
		EventHandler.on_pre_save(view)

	def on_pre_save_async(self, view):
		EventHandler.on_pre_save_async(view)

	def on_post_save(self, view):
		EventHandler.on_post_save(view)

	def on_post_save_async(self, view):
		EventHandler.on_post_save_async(view)

	def on_modified(self, view):
		EventHandler.on_modified(view)

	def on_modified_async(self, view):
		EventHandler.on_modified_async(view)

	def on_selection_modified(self, view):
		EventHandler.on_selection_modified(view)

	def on_selection_modified_async(self, view):
		EventHandler.on_selection_modified_async(view)

	def on_activated(self, view):
		EventHandler.on_activated(view)

	def on_activated_async(self, view):
		EventHandler.on_activated_async(view)

	def on_deactivated(self, view):
		EventHandler.on_deactivated(view)

	def on_deactivated_async(self, view):
		EventHandler.on_deactivated_async(view)
