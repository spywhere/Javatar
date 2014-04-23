import sublime
import os
import pty
import select
import threading
from time import clock
from subprocess import Popen, STDOUT

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
		read_master, read_slave = pty.openpty()
		write_master, write_slave = pty.openpty()
		proc = Popen(self.cmds, bufsize=1, stdin=write_slave, stdout=read_slave, stderr=STDOUT, close_fds=True, cwd=self.cwd)
		proper = False
		self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
		self.data_in = ""
		self.skip = False
		while self.view is not None and self.view.window() is not None:
			read_ready, write_ready, _ = select.select([read_master], [write_master], [], 0.04)
			if len(self.old_data) < self.view.size():
				self.data_in = self.view.substr(sublime.Region(len(self.old_data), self.view.size()))
			elif len(self.old_data) > self.view.size():
				self.skip = True
				self.view.run_command("javatar_util", {"util_type": "clear"})
				self.view.run_command("javatar_util", {"util_type": "add", "text": self.old_data})
			else:
				self.skip = False
			if read_ready:
				data = os.read(read_master, 512)
				if not data:
					break
				self.last_line = data.decode("UTF-8").replace("\r\n","\n").strip()
				self.view.run_command("javatar_util", {"util_type": "add", "text": data.decode("UTF-8").replace("\r\n","\n")})
				self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
				if self.to_console:
					print(data.decode("UTF-8").replace("\r\n","\n"))
			if write_ready:
				if self.data_in is not None and "\n" in self.data_in:
					os.write(write_master, self.data_in.encode("UTF-8"))
			if proc.poll() is not None:
				proper = True
				break
		os.close(write_master)
		os.close(write_slave)
		os.close(read_slave)
		os.close(read_master)
		proc.wait()
		self.result = True
		if self.on_complete is not None:
			self.on_complete(clock()-start_time, proper)

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
		read_master, read_slave = pty.openpty()
		proc = Popen(self.cmds, bufsize=1, stdout=read_slave, stderr=STDOUT, close_fds=True, cwd=self.cwd)
		while True:
			read_ready, _, _ = select.select([read_master], [], [], 0.04)
			if read_ready:
				data = os.read(read_master, 512)
				if not data:
					break
				if self.data_out is None:
					self.data_out = data.decode("UTF-8").replace("\r\n","\n")
				else:
					self.data_out += data.decode("UTF-8").replace("\r\n","\n")
				if self.to_console:
					print(data.decode("UTF-8").replace("\r\n","\n"))
			if proc.poll() is not None:
				break
		os.close(read_slave)
		os.close(read_master)
		proc.wait()
		self.result = True
		if self.on_complete is not None:
			self.on_complete(clock()-start_time, self.data_out)