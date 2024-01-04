class GoalSorting:
	SEQUENTIAL = 1
	TYPE_THEN_DEPTH = 2
	DEPTH_THEN_TYPE = 3

	@staticmethod
	def toString(pGoalSortingValue : int) -> str:
		if pGoalSortingValue == GoalSorting.SEQUENTIAL: return 'SEQUENTIAL'
		if pGoalSortingValue == GoalSorting.TYPE_THEN_DEPTH: return 'TYPE_THEN_DEPTH'
		if pGoalSortingValue == GoalSorting.DEPTH_THEN_TYPE: return 'DEPTH_THEN_TYPE'
		return None