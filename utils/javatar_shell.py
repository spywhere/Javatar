import sublime
import os
import sys
import threading
import subprocess
from time import clock, sleep
from .javatar_utils import get_settings


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
        while True:
            data = os.read(self.proc.stdout.fileno(), 512)
            if len(data) > 0:
                _, layout_height = self.view.layout_extent()
                _, viewport_height = self.view.viewport_extent()
                viewport_posx, viewport_posy = self.view.viewport_position()
                decoded_data = data.decode("utf-8", get_settings("encoding_handle")).replace("\r\n", "\n")
                self.view.run_command("javatar_util", {"util_type": "add", "text": decoded_data})
                self.old_data += decoded_data
                if get_settings("autoscroll_to_bottom") and viewport_posy >= layout_height - viewport_height - get_settings("autoscroll_snap_range"):
                    _, layout_height = self.view.layout_extent()
                    self.view.set_viewport_position((viewport_posx, layout_height - viewport_height), False)
                if self.to_console:
                    print(decoded_data)
            elif self.proc.poll() is not None:
                break
            sleep(get_settings("shell_refresh_interval"))
        self.isReadable = False

    def read_stdin(self):
        while self.proc.poll() is None:
            # If input make output less than before, reset it
            if len(self.old_data) > self.view.size():
                self.view.run_command("javatar_util", {"util_type": "clear"})
                self.view.run_command("javatar_util", {"util_type": "add", "text": self.old_data})
            elif len(self.old_data) < self.view.size():
                self.data_in = self.view.substr(sublime.Region(len(self.old_data), self.view.size()))
            if "\n" in self.data_in:
                os.write(self.proc.stdin.fileno(), self.data_in.encode("UTF-8"))
                self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
                self.data_in = ""
            sleep(get_settings("shell_refresh_interval"))
        self.isWritable = False

    def run(self):
        start_time = clock()
        self.proc = self.popen(self.cmds, self.cwd)
        self.old_data = self.view.substr(sublime.Region(0, self.view.size()))
        self.data_in = ""
        self.return_code = None
        self.isReadable = True
        self.isWritable = True

        threading.Thread(target=self.read_stdout).start()
        threading.Thread(target=self.read_stdin).start()

        while self.view is not None and self.view.window() is not None:
            if self.proc.poll() is not None:
                self.return_code = self.proc.poll()
            if not self.isWritable and not self.isReadable:
                self.proc.stdout.close()
                self.proc.stdin.close()
                break
            sleep(get_settings("shell_refresh_interval"))
        if self.return_code is None:
            self.kill(self.proc)
        self.result = True
        if self.on_complete is not None:
            self.on_complete(clock() - start_time, self.return_code, self.params)


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
        while True:
            data = os.read(self.proc.stdout.fileno(), 512)
            if len(data) > 0:
                decoded_data = data.decode("utf-8", get_settings("encoding_handle")).replace("\r\n", "\n")
                if self.data_out is None:
                    self.data_out = decoded_data
                else:
                    self.data_out += decoded_data
                if self.to_console:
                    print(decoded_data)
            elif self.proc.poll() is not None:
                break
            sleep(get_settings("shell_refresh_interval"))
        self.isReadable = False

    def run(self):
        start_time = clock()
        self.proc = self.popen(self.cmds, self.cwd)
        self.return_code = None
        self.isReadable = True

        threading.Thread(target=self.read_stdout).start()

        while True:
            if self.proc.poll() is not None:
                self.return_code = self.proc.poll()
            if not self.isReadable:
                self.proc.stdout.close()
                break
            sleep(get_settings("shell_refresh_interval"))
        if self.return_code is None:
            self.kill(self.proc)
        self.result = True
        if self.on_complete is not None:
            self.on_complete(clock() - start_time, self.data_out, self.return_code, self.params)


class JavatarBlockShell():
    def run(self, cmds, cwd=None):
        start_time = clock()
        self.proc = self.popen(cmds, cwd)
        self.return_code = None
        self.data_out = None
        self.isReadable = True

        threading.Thread(target=self.read_stdout).start()

        while True:
            if self.proc.poll() is not None:
                self.return_code = self.proc.poll()
            if not self.isReadable:
                self.proc.stdout.close()
                break
            sleep(get_settings("shell_refresh_interval"))
        if self.return_code is None:
            self.kill(self.proc)
        return {"elapse_time": clock() - start_time, "data": self.data_out, "return_code": self.return_code}

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
                decoded_data = data.decode("utf-8", get_settings("encoding_handle")).replace("\r\n", "\n")
                if self.data_out is None:
                    self.data_out = decoded_data
                else:
                    self.data_out += decoded_data
            elif self.proc.poll() is not None:
                break
            sleep(get_settings("shell_refresh_interval"))
        self.isReadable = False
