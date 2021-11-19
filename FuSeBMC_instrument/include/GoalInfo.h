#ifndef GOALINFO_H
#define GOALINFO_H

class GoalInfo
{
	public:
		unsigned long int goal = 0;
		unsigned long int depth = 0;
		unsigned long int funcID = 0;
		GoalInfo(unsigned long int p_goal, unsigned long int p_depth, unsigned long int p_funcID);
		
};


#endif /* GOALINFO_H */

