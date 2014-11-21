import sublime
import sublime_plugin
import threading
import traceback
import os
from ..utils import *


class JavatarInstallCommand(sublime_plugin.WindowCommand):
    action = "invalid"

    def run(self, installtype=None, name=None, filename=None, url=None, checksum=None):
        if installtype is not None:
            add_action(
                "javatar.command.install.run",
                "Install Package [type={}, name={}]".format(
                    installtype,
                    name
                )
            )
            self.pname = name
            if installtype == "remote_package":
                self.action = "install"
                thread = JavatarRemotePackageInstallerThread(name, filename, url, checksum, self.on_complete)
                thread.start()
                ThreadProgress(thread, "Installing Javatar package \"" + name + "\"", "Javatar package \"" + name + "\" has been successfully installed")
            elif installtype == "uninstall_package":
                self.action = "uninstall"
                thread = JavatarPackageUninstallerThread(name, filename, self.on_complete)
                thread.start()
                ThreadProgress(thread, "Uninstalling Javatar package \"" + name + "\"", "Javatar package \"" + name + "\" has been successfully uninstalled")

    def getPackageData(self):
        data = {}
        data["SchemaVersion"] = get_schema_version()
        data["PackageAction"] = self.action
        data["PackageName"] = self.pname
        data["SublimeVersion"] = str(sublime.version())
        data["Platform"] = sublime.platform()
        return data

    def on_complete(self):
        send_package_action(self.getPackageData())
        reset_packages()
        no_require = False
        if self.action == "uninstall":
            no_require = True
        load_packages(no_require)


class JavatarPackageUninstallerThread(threading.Thread):
    def __init__(self, name, filename, on_complete=None):
        self.pkgname = name
        if filename[0:8] == "Packages":
            self.filename = sublime.packages_path() + filename[8:]
        else:
            self.filename = filename
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def run(self):
        try:
            os.remove(self.filename)
            self.result = True
            if self.on_complete is not None:
                sublime.set_timeout(self.on_complete, 3000)
        except Exception as e:
            self.result_message = "Javatar package \"" + self.pkgname + "\" uninstallation has failed: " + str(e)
            traceback.print_exc()
            self.result = False


class JavatarRemotePackageInstallerThread(threading.Thread):
    def __init__(self, name, filename, url, checksum, on_complete=None):
        self.pkgname = name
        self.filename = filename
        self.url = url
        self.checksum = checksum
        self.on_complete = on_complete
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.result_message = "Javatar package \"" + self.pkgname + "\" has been corrupted"
            urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()))
            data = urllib.request.urlopen(self.url + self.filename + ".javatar-packages").read()
            datahash = hashlib.sha256(data).hexdigest()
            if self.checksum != datahash:
                self.result = False
                return
            open(join(sublime.packages_path(), "user", self.filename + ".javatar-packages"), "wb").write(data)
            self.result = True
            if self.on_complete is not None:
                sublime.set_timeout(self.on_complete, 3000)
        except Exception as e:
            self.result_message = "Javatar package \"" + self.pkgname + "\" installation has failed: " + str(e)
            traceback.print_exc()
            self.result = False
