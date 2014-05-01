import sublime
import re
import os
import threading
from .javatar_shell import *
from .javatar_thread import *
from .javatar_utils import *


# JDK Path both global and project


def detect_jdk(silent=False, on_done=None, progress=False):
	thread = JavatarJDKDetectionThread(silent, on_done)
	thread.start()
	if progress:
		ThreadProgress(thread, "Javatar is detecting installed JDK", "Javatar has finished JDK detection")


def normalize_package(package):
	while package.startswith("."):
		package = package[1:]
	return re.sub("\\.*$", "", package)


def get_all_types(packageImports):
	imports = []
	if "package" in packageImports:
		if "interface" in packageImports:
			imports += packageImports["interface"]
		if "class" in packageImports:
			imports += packageImports["class"]
		if "enum" in packageImports:
			imports += packageImports["enum"]
		if "exception" in packageImports:
			imports += packageImports["exception"]
		if "error" in packageImports:
			imports += packageImports["error"]
		if "type" in packageImports:
			imports += packageImports["type"]
		if "annotation" in packageImports:
			imports += packageImports["annotation"]
	else:
		if "interface" in packageImports:
			for interface in packageImports["interface"]:
				imports.append(interface["name"])
		if "class" in packageImports:
			for clazz in packageImports["class"]:
				imports.append(clazz["name"])
		if "enum" in packageImports:
			for enum in packageImports["enum"]:
				imports.append(enum["name"])
		if "exception" in packageImports:
			for exception in packageImports["exception"]:
				imports.append(exception["name"])
		if "error" in packageImports:
			for error in packageImports["error"]:
				imports.append(error["name"])
		if "type" in packageImports:
			for types in packageImports["type"]:
				imports.append(types["name"])
		if "annotation" in packageImports:
			for annotation in packageImports["annotation"]:
				imports.append(annotation["name"])
	return imports


def find_class(path, classname):
	# If it is a default class, should import manually
	from .javatar_collections import get_packages
	classes = []
	foundClass = False
	for root, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename == classname + ".java":
				classpath = to_package(without_extension(os.path.join(root, filename)))
				classes.append(classpath)
				foundClass = True
	for packageImport in get_packages():
		if "packages" in packageImport:
			for packageName in packageImport["packages"]:
				package = packageImport["packages"][packageName]
				if not foundClass and "default" in package and package["default"]:
					continue
				if classname in get_all_types(package):
					classes.append(packageName+"."+classname)
	classes.sort()
	return classes


def get_package_path(text):
	return normalize_package(re.search(get_settings("package_match"), text, re.M).group(0))


def get_class_name_by_regex(text):
	return re.search(get_settings("package_class_match"), text, re.M).group(0)


def package_as_directory(package):
	return merge_path(package.split("."))


def make_package(current_dir, package, silent=False):
	target_dir = get_path("join", current_dir, package_as_directory(package))
	if not os.path.exists(target_dir):
		try:
			os.makedirs(target_dir)
		except BaseException as e:
			sublime.error_message("Error while create a package: " + str(e))
	else:
		if not silent:
			sublime.message_dialog("Package is already exists")
	return target_dir


def get_latest_jdk(jdks=None):
	jdk_version = []
	for jdk in jdks:
		if jdk == "use":
			continue
		jdk_version.append(jdk)
	if len(jdk_version) > 0:
		jdk_version.sort(reverse=True)
		return jdk_version[0]
	return None


def get_read_version(version=None):
	if version is None:
		return version
	v = "JDK"+version["version"]
	if "update" in version:
		v += "u"+version["update"]
	return v


def get_java_version(path="", check_all=False, executable=None):
	if executable is None:
		if check_all:
			all_version = None
			for exe in get_settings("java_executables"):
				executable = get_executable(exe, path)
				version = get_java_version(path, False, executable)
				if version is None:
					return None
				elif all_version is None:
					all_version = version
			return all_version
		else:
			executable = get_executable("version", path)
	if executable is None:
		return None
	output = JavatarBlockShell().run(executable+" -version")
	if output["data"] is not None:
		match = re.search(get_settings("java_version_match"), output["data"])
		if match is not None:
			version = {}
			if match.lastindex > 0:
				version["version"] = match.group(1)
				if match.lastindex > 1:
					version["update"] = match.group(2)
			return version
	return None


def dict_to_list(dicto):
	olist = []
	for key in dicto:
		olist.append(dicto[key])
	return olist


def is_jdk_dir(path):
	required_files = dict_to_list(get_settings("java_executables"))
	for name in os.listdir(path):
		pathname = os.path.join(path, name)
		if os.path.isfile(pathname):
			filename, ext = os.path.splitext(name)
			while filename in required_files and (ext == "" or ext == ".exe"):
				required_files.remove(filename)
	return len(required_files) <= 0


def get_jdk_dirs(path):
	jdk_dirs = {}

	for name in os.listdir(path):
		pathname = os.path.join(path, name)
		if os.path.isdir(pathname):
			if is_jdk_dir(pathname):
				version = get_java_version(pathname)
				if version is not None:
					jdk = {
						"path": pathname,
						"version": version["version"]
					}
					if "update" in version:
						jdk["update"] = version["update"]
					jdk_dirs[get_read_version(version)] = jdk
			dirs = get_jdk_dirs(pathname)
			for key in dirs:
				jdk_dirs[key] = dirs[key]
	return jdk_dirs


def get_default_jdk(jdks=None):
	if jdks is None:
		jdks = JavatarMergedDict(get_global_settings("jdk_version"), get_project_settings("jdk_version"))
	if not jdks.has("use"):
		return None
	if jdks.get("use") == "":
		return {"path":""}
	elif jdks.has(jdks.get("use")):
		return jdks.get(jdks.get("use"))
	return None


def verify_jdk(jdks=None, listener=None):
	if jdks is None:
		jdks = JavatarMergedDict(get_global_settings("jdk_version"), get_project_settings("jdk_version"))
	if jdks.has("use"):
		if jdks.get("use") == "":
			version = get_read_version(get_java_version(check_all=True))
			if version is None:
				jdks.set("use", None)
				return verify_jdk(jdks, listener)
			else:
				if listener is not None:
					listener("default_checked", version)
				return jdks
		if jdks.has(jdks.get("use")):
			jdk = jdks.get(jdks.get("use"))
			if "path" in jdk and "version" in jdk:
				if not os.path.exists(jdk["path"]) or not is_jdk_dir(jdk["path"]):
					jdks.set(jdks.get("use"), None)
					jdks.set("use", None)
					return verify_jdk(jdks, listener)
				if listener is not None:
					listener("selected", get_read_version(jdk))
				return jdks
		jdks.set(jdks.get("use"), None)
		jdks.set("use", None)
		return verify_jdk(jdks, listener)
	platform = sublime.platform()
	installation_path = get_settings("jdk_installation")
	default_java = get_read_version(get_java_version(check_all=True))
	if default_java is None:
		if listener is not None:
			listener("no_default", None)
	else:
		jdks.set("use", "")
		if listener is not None:
			listener("default_detected", default_java)

	if platform in installation_path:
		for path in installation_path[platform]:
			if os.path.exists(path) and os.path.isdir(path):
				dirs = get_jdk_dirs(path)
				for key in dirs:
					jdks.set(key, dirs[key])
	if not jdks.has("use") and jdks.get_dict() is not None:
		latest_jdk = get_latest_jdk(jdks.get_dict())
		if latest_jdk is None:
			return None
		if listener is not None:
			listener("latest", latest_jdk)
		jdks.set("use", latest_jdk)
	return jdks


def get_executable(name, path=None):
	if name not in get_settings("java_executables"):
		return None
	if path is None:
		jdk = get_default_jdk()
		if jdk is None:
			return jdk
		else:
			path = jdk["path"]
	return "\""+os.path.join(path, get_settings("java_executables")[name])+"\""


class JavatarJDKDetectionThread(threading.Thread):
	def __init__(self, silent=False, on_done=None):
		self.silent = silent
		self.on_done = on_done
		threading.Thread.__init__(self)

	def listener(self, detection, version):
		if self.silent:
			return
		if detection == "default_checked" or detection == "default_detected":
			print("[Javatar] Use default Java version [" + version + "]")
		elif detection == "selected":
			print("[Javatar] Use " + version)
		elif detection == "latest":
			print("[Javatar] Use latest installed version [" + version + "]")
		elif is_debug():
			print("JDK Detection: " + detection)

	def run(self, renew=False):
		try:
			jdks = verify_jdk(None, self.listener)
			if jdks is not None and jdks.get_dict() is not None:
				if jdks.get_global_dict() is not None:
					set_settings("jdk_version", jdks.get_global_dict())
				else:
					del_settings("jdk_version")
				if jdks.get_local_dict() is not None:
					set_settings("jdk_version", jdks.get_local_dict(), True)
				else:
					del_settings("jdk_version", True)
			else:
				del_settings("jdk_version")
				del_settings("jdk_version", True)
				print("[Javatar] No JDK found")
				sublime.error_message("Javatar cannot find JDK installed in your computer.\n\nPlease install or settings the location of installed JDK.")
			if self.on_done is not None:
				self.on_done()
			self.result = True
		except Exception as e:
			print("JDK Detection Error: " + str(e))
			self.result = False