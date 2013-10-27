import sublime_plugin
import sublime
import re
from ..utils import *


class JavatarCompletions(sublime_plugin.EventListener):
	def getCallPosition(self, view, pos):
		if pos <=0:
			return 0
		if view.substr(sublime.Region(pos-1, pos)) == ")":
			while view.substr(sublime.Region(pos-1, pos)) != "(":
				pos-=1
			return self.getCallPosition(view, pos)
		elif view.substr(sublime.Region(pos-1, pos)) != " " and view.substr(sublime.Region(pos-1, pos)) != ";":
			return self.getCallPosition(view, pos-1)
		return pos

	def on_query_completions(self, view, prefix, locations):
		if not isDebug() or isStable() or not view.match_selector(locations[0], "source.java"): return []

		cursorPos = locations[0]
		callPos = self.getCallPosition(view, cursorPos)
		#Find call statement
		callStatement = view.substr(sublime.Region(callPos, cursorPos))
		#Minimized method call
		minCall = re.sub(getSettings("method_replacement"), "()", callStatement)
		view.window().show_quick_panel([[callStatement, "Method call"], [minCall, "Minimized method call"]], "")
		return []