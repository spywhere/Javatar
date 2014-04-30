import sublime
import os, sys
import threading
import subprocess
from time import clock


class JavatarShell(threading.Thread):
	def __init__(self, cmds, view, on_complete=None, to_console=False, params=None):
		self.params = params
		self.cmds = cmds
		self.on_complete = on_complete
		self.view = view
		self.to_console = to_console
		self.cwd = None
		threading.Thread.__init__(self)

	def set_cwd(self, path=""):
		self.cwd = path

	def popen(self, cmd, cwd):
		if sys.platform == "win32":
			return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=True)
		elif sys.platform == "darwin":
			return subprocess.Popen(["/bin/bash", "-l", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)
		elif sys.platform == "linux":
			return subprocess.Popen(["/bin/bash", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)
		else:
			return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)

	def kill(self, proc):
		if sys.platform == "win32":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			subprocess.Popen("taskkill /PID " + str(proc.pid), startupinfo=startupinfo)
		else:
			proc.terminate()

	def read_stdout(self):
		while self.proc.poll() is None:
			data = os.read(self.proc.stdout.fileno(), 512)
			if len(data) > 0:
				self.read_only = False
				self.view.run_command("javatar_util", {"util_type": "add", "text": data.decode("UTF-8").replace("\r\n","\n")})
				self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
				if self.to_console:
					print(data.decode("UTF-8").replace("\r\n","\n"))

	def read_stdin(self):
		while self.proc.poll() is None:
			if "\n" in self.data_in:
				os.write(self.proc.stdin.fileno(), self.data_in.encode("UTF-8"))
				self.data_in = ""

	def run(self):
		start_time = clock()
		self.proc = self.popen(self.cmds, self.cwd)
		self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
		self.data_in = ""
		self.return_code = None
		self.read_only = True

		threading.Thread(target=self.read_stdout).start()
		threading.Thread(target=self.read_stdin).start()

		while self.view is not None and self.view.window() is not None:
			if len(self.old_data) < self.view.size():
				self.data_in = self.view.substr(sublime.Region(len(self.old_data), self.view.size()))
			if self.read_only or len(self.old_data) > self.view.size():
				self.view.run_command("javatar_util", {"util_type": "clear"})
				self.view.run_command("javatar_util", {"util_type": "add", "text": self.old_data})

			if self.proc.poll() is not None:
				self.return_code = self.proc.poll()
				self.proc.stdout.close()
				self.proc.stdin.close()
				break
		if self.return_code is None:
			self.kill(self.proc)
		self.result = True
		if self.on_complete is not None:
			self.on_complete(clock()-start_time, self.return_code, self.params)

class JavatarSilentShell(threading.Thread):
	def __init__(self, cmds, on_complete=None, to_console=False, params=None):
		self.params = params
		self.cmds = cmds
		self.on_complete = on_complete
		self.to_console = to_console
		self.cwd = None
		self.data_out = None
		threading.Thread.__init__(self)

	def set_cwd(self, path=""):
		self.cwd = path

	def popen(self, cmd, cwd):
		if sys.platform == "win32":
			return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=True)
		elif sys.platform == "darwin":
			return subprocess.Popen(["/bin/bash", "-l", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)
		elif sys.platform == "linux":
			return subprocess.Popen(["/bin/bash", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)
		else:
			return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)

	def kill(self, proc):
		if sys.platform == "win32":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			subprocess.Popen("taskkill /PID " + str(proc.pid), startupinfo=startupinfo)
		else:
			proc.terminate()

	def read_stdout(self):
		while self.proc.poll() is None:
			data = os.read(self.proc.stdout.fileno(), 512)
			if len(data) > 0:
				if self.data_out is None:
					self.data_out = data.decode("UTF-8").replace("\r\n","\n")
				else:
					self.data_out += data.decode("UTF-8").replace("\r\n","\n")
				if self.to_console:
					print(data.decode("UTF-8").replace("\r\n","\n"))

	def run(self):
		start_time = clock()
		self.proc = self.popen(self.cmds, self.cwd)
		self.return_code = None

		threading.Thread(target=self.read_stdout).start()

		while True:
			if self.proc.poll() is not None:
				self.return_code = self.proc.poll()
				self.proc.stdout.close()
				break
		if self.return_code is None:
			self.kill(self.proc)
		self.result = True
		if self.on_complete is not None:
			self.on_complete(clock()-start_time, self.data_out, self.return_code, self.params)

class JavatarBlockShell():
	def run(self, cmds, cwd=None):
		start_time = clock()
		self.proc = self.popen(cmds, cwd)
		self.return_code = None
		self.data_out = None

		threading.Thread(target=self.read_stdout).start()

		while True:
			if self.proc.poll() is not None:
				self.return_code = self.proc.poll()
				self.proc.stdout.close()
				break
		if self.return_code is None:
			self.kill(self.proc)
		return {"elapse_time": clock()-start_time, "data": self.data_out, "return_code": self.return_code}

	def popen(self, cmd, cwd):
		if sys.platform == "win32":
			return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=True)
		elif sys.platform == "darwin":
			return subprocess.Popen(["/bin/bash", "-l", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)
		elif sys.platform == "linux":
			return subprocess.Popen(["/bin/bash", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)
		else:
			return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=False)

	def kill(self, proc):
		if sys.platform == "win32":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			subprocess.Popen("taskkill /PID " + str(proc.pid), startupinfo=startupinfo)
		else:
			proc.terminate()

	def read_stdout(self):
		while self.proc.poll() is None:
			data = os.read(self.proc.stdout.fileno(), 512)
			if len(data) > 0:
				if self.data_out is None:
					self.data_out = data.decode("UTF-8").replace("\r\n","\n")
				else:
					self.data_out += data.decode("UTF-8").replace("\r\n","\n")
