import sublime_plugin
import sublime
import re
from ..utils import *


'''
Method Call Completion Process
 1. Get call statement
 2. Find class contains that call from type and imports
 3. If 2 is not found, find in default imports
 4. If 3 is not found, return nothing
 5. If 2 or 3 is found, return all methods that start with call, with arguments-ready. If class inherited from another class, find them too!

Work to do!
Invent a selector system

get_regions(selector, file_scope)
 - selector: class, number, etc.
 - file_scope: project, package, subpackage, class

List "all" methods and "all" unprivate fields within "all" Java's classes in "all" packages

Keywords:
this,super
'''


class JavatarCompletions(sublime_plugin.EventListener):
    def getCallPosition(self, view, pos):
        if pos <= 0:
            return 0
        if view.substr(sublime.Region(pos - 1, pos)) == ")":
            while view.substr(sublime.Region(pos - 1, pos)) != "(":
                pos -= 1
            return self.getCallPosition(view, pos)
        elif view.substr(sublime.Region(pos - 1, pos)) != " " and view.substr(sublime.Region(pos - 1, pos)) != ";":
            return self.getCallPosition(view, pos - 1)
        return pos

    def on_query_completions(self, view, prefix, locations):
        if not is_debug() or is_stable() or not view.match_selector(locations[0], "source.java"):
            return []

        cursorPos = locations[0]
        callPos = self.getCallPosition(view, cursorPos)
        #Find call statement
        callStatement = view.substr(sublime.Region(callPos, cursorPos))
        #Minimized method call
        minCall = re.sub(get_settings("method_replacement"), "()", callStatement)
        view.window().show_quick_panel([[callStatement, "Method call"], [minCall, "Minimized method call"]], "")
        return []
