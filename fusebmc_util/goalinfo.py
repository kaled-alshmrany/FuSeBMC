from .goaltype import GoalType

class GoalInfo:
	def __init__(self,goal = 0, goalType = GoalType.NONE, depth = -1,globalDepth = -1,funcID = 0):
		self.goal = goal
		self.goalType = goalType
		self.depth = depth
		self.correspondingDepth = depth
		self.globalDepth = globalDepth
		self.funcID = funcID
		
	def toString(self):
		s = '(GOAL_' + str(self.goal)
		if self.goalType != GoalType.NONE : s += ',' + GoalType.GetAsString(self.goalType)
		if(self.depth != -1) : s += ', Local Depth=' + str(self.depth)
		if(self.globalDepth != -1) : s += ', Global Depth=' + str(self.globalDepth)
		s += ')'
		return s
	def __repr__(self):
		return self.toString()
	def __str__(self):
		return self.toString()
