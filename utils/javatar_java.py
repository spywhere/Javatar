import os
import re
import sublime


def normalizePackage(package):
    while package.startswith("."):
        package = package[1:]
    return re.sub("\\.*$", "", package)


def getPackagePath(text):
    from .javatar_utils import getSettings
    return normalizePackage(re.search(getSettings("package_match"), text, re.I | re.M).group(0))


def getClassName(text):
    from .javatar_utils import getSettings
    return re.search(getSettings("class_match"), text, re.I | re.M).group(0)


def packageAsDirectory(package):
    return "/".join(package.split("."))


def makePackage(current_dir, package, silent=False):
    from .javatar_utils import getPath
    target_dir = getPath("join", current_dir, packageAsDirectory(package))
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
        except BaseException as e:
            sublime.error_message("Error while create a package: " + str(e))
    else:
        if not silent:
            sublime.message_dialog("Package is already exists")
    return target_dir
