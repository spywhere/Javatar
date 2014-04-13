import sublime

class ThreadProgress():
	def __init__(self, thread, message, success_message, anim_fx=None):
		self.thread = thread
		self.message = message
		self.success_message = success_message
		if anim_fx is not None:
			self.anim_fx = anim_fx
		sublime.set_timeout(lambda: self.run(0), 100)

	def anim_fx(self, i, message, thread):
		return {"i": (i+1) % 3, "message": "%s %s" % (self.message, "." * (i+1)), "delay": 300}

	def run(self, i):
		if not self.thread.is_alive():
			if hasattr(self.thread, "result") and not self.thread.result:
				if hasattr(self.thread, "result_message"):
					sublime.status_message(self.thread.result_message)
				else:
					sublime.status_message("")
				return
			sublime.status_message(self.success_message)
			return
		info = self.anim_fx(i, self.message, self.thread)
		sublime.status_message(info["message"])
		sublime.set_timeout(lambda: self.run(info["i"]), info["delay"])

class SilentThreadProgress():
	def __init__(self, thread, on_complete):
		self.thread = thread
		self.on_complete = on_complete
		sublime.set_timeout(lambda: self.run(), 100)

	def run(self):
		if not self.thread.is_alive():
			self.on_complete(self.thread)
			if hasattr(self.thread, "result") and not self.thread.result:
				if hasattr(self.thread, "result_message"):
					sublime.status_message(self.thread.result_message)
				else:
					sublime.status_message("")
			return
		sublime.set_timeout(lambda: self.run(), 100)