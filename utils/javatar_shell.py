import sublime
import os, sys
import select
import threading
import subprocess
from time import clock


class JavatarShell(threading.Thread):
	def __init__(self, cmds, view, on_complete=None, to_console=False):
		self.cmds = cmds
		self.on_complete = on_complete
		self.view = view
		self.to_console = to_console
		self.cwd = None
		threading.Thread.__init__(self)

	def set_cwd(self, path=""):
		self.cwd = path

	def run(self):
		start_time = clock()
		proc = subprocess.Popen(self.cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True, cwd=self.cwd)
		self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
		self.data_in = ""
		self.return_code = None
		read_only = True

		while self.view is not None and self.view.window() is not None:
			read_ready, write_ready, _ = select.select([proc.stdout.fileno()], [proc.stdin.fileno()], [], 0.04)
			if len(self.old_data) < self.view.size():
				self.data_in = self.view.substr(sublime.Region(len(self.old_data), self.view.size()))
			if read_only or len(self.old_data) > self.view.size():
				self.view.run_command("javatar_util", {"util_type": "clear"})
				self.view.run_command("javatar_util", {"util_type": "add", "text": self.old_data})

			if read_ready and proc.stdout:
				read_only = False
				data = os.read(proc.stdout.fileno(), 512)
				if not data:
					break
				self.view.run_command("javatar_util", {"util_type": "add", "text": data.decode("UTF-8").replace("\r\n","\n")})
				self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
				if self.to_console:
					print(data.decode("UTF-8").replace("\r\n","\n"))
			if write_ready and proc.stdin:
				if self.data_in is not None and "\n" in self.data_in:
					os.write(proc.stdin.fileno(), self.data_in.encode("UTF-8"))
					self.data_in = ""
			if proc.poll() is not None:
				self.return_code = proc.poll()
				proc.stdout.close()
				proc.stdin.close()
				break
		if self.return_code is None:
			proc.kill()
		self.result = True
		if self.on_complete is not None:
			self.on_complete(clock()-start_time, self.return_code)

class JavatarSilentShell(threading.Thread):
	def __init__(self, cmds, on_complete=None, to_console=False):
		self.cmds = cmds
		self.on_complete = on_complete
		self.to_console = to_console
		self.cwd = None
		self.data_out = None
		threading.Thread.__init__(self)

	def set_cwd(self, path=""):
		self.cwd = path

	def run(self):
		start_time = clock()
		proc = subprocess.Popen(self.cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True, cwd=self.cwd)
		self.return_code = None

		while True:
			read_ready, _, _ = select.select([proc.stdout.fileno()], [], [], 0.04)

			if read_ready and proc.stdout:
				data = os.read(proc.stdout.fileno(), 512)
				if not data:
					break
				if self.data_out is None:
					self.data_out = data.decode("UTF-8").replace("\r\n","\n")
				else:
					self.data_out += data.decode("UTF-8").replace("\r\n","\n")
				if self.to_console:
					print(data.decode("UTF-8").replace("\r\n","\n"))
			if proc.poll() is not None:
				self.return_code = proc.poll()
				proc.stdout.close()
				break
		if self.return_code is None:
			proc.kill()
		self.result = True
		if self.on_complete is not None:
			self.on_complete(clock()-start_time, self.data_out, self.return_code)
