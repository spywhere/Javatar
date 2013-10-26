class ActionList:
	actions = []

	def addAction(self, name, action):
		from .javatar_utils import isReady, getSettings
		if isReady() and getSettings("enable_actions_history"):
			self.actions.append([name, action])
		elif not isReady():
			self.actions.append([name, action])

	def isStartswith(self, key, list):
		for e in list:
			if key.startswith(e):
				return True
		return False

	def getAction(self, include=[], exclude=[]):
		out = []
		for action in self.actions:
			if (len(include) <= 0 or self.isStartswith(action[0], include)) and (len(exclude) <= 0 or not self.isStartswith(action[0], exclude)):
				out.append(action[1])
		return out

	def clearAction(self):
		self.actions = {}

ACTION = None

def getAction():
	global ACTION
	if ACTION is None:
		ACTION = ActionList()
	return ACTION