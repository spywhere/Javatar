import os
import re
import sublime


def normalizePackage(package):
    while package.startswith("."):
        package = package[1:]
    return re.sub("\\.*$", "", package)


def analyseJavaContents(contents):
    from .javatar_utils import getSettings
    packageScope = re.search(getSettings("package_name_prefix")+getSettings("package_name_scope")+getSettings("package_name_suffix"), contents, re.M).group(0)
    classScope = re.search(getSettings("class_name_prefix")+getSettings("class_name_scope")+getSettings("class_name_suffix"), contents, re.M).group(0)
    packageScope = re.sub(getSettings("package_name_prefix"), "", packageScope)
    packageScope = re.sub(getSettings("package_name_suffix"), "", packageScope)
    classScope = re.sub(getSettings("class_name_prefix"), "", classScope)
    classScope = re.sub(getSettings("class_name_suffix"), "", classScope)
    return {"package": packageScope, "class": classScope}


def getPackagePath(text):
    from .javatar_utils import getSettings
    return normalizePackage(re.search(getSettings("package_match"), text, re.M).group(0))


def getClassName(text):
    from .javatar_utils import getSettings
    return re.search(getSettings("package_class_match"), text, re.M).group(0)


def packageAsDirectory(package):
    from .javatar_utils import mergePath
    return mergePath(package.split("."))


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
