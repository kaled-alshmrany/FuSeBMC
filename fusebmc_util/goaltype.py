class GoalType:
	IF = 1
	ELSE = 2
	FOR = 3
	CXX_FOR_RANGE = 4
	DO_WHILE = 5
	WHILE = 6
	COMPOUND = 7
	LOOP = 8
	END_OF_FUNCTION = 9
	AFTER_LOOP = 10
	EMPTY_ELSE = 11
	NONE = 12
	
	@staticmethod
	def GetAsString(goalType):
		if goalType == GoalType.IF: return 'IF'
		if goalType == GoalType.ELSE: return 'ELSE'
		if goalType == GoalType.FOR: return 'FOR'
		if goalType == GoalType.CXX_FOR_RANGE : return 'CXX_FOR_RANGE'
		if goalType == GoalType.DO_WHILE: return 'DO_WHILE'
		if goalType == GoalType.WHILE: return 'WHILE'
		if goalType == GoalType.COMPOUND: return 'COMPOUND'
		if goalType == GoalType.LOOP: return 'LOOP'
		if goalType == GoalType.END_OF_FUNCTION : return 'END_OF_FUNCTION'
		if goalType == GoalType.AFTER_LOOP: return 'AFTER_LOOP'
		if goalType == GoalType.EMPTY_ELSE : return 'EMPTY_ELSE'
		if goalType == GoalType.NONE: return 'NONE'
