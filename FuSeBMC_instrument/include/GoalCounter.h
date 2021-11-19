#ifndef GOALCOUNTER_H
#define GOALCOUNTER_H

#include <map>
#include <string>
#include <vector>
#include <FuSeBMC_instrument.h>
#include <NonDetCallInfo.h>
#include <GoalInfo.h>
#include <clang/AST/Decl.h>




class GoalCounter
{

	private:
		static GoalCounter instance;
		GoalCounter();
		std::string GetNewGoalForFunc(std::string func,GoalType goalType);

	public:
		map<string,vector<string>> * funcLabelMap;
		vector<unsigned long int> *  vctIFGoals;
		vector<unsigned long int> *  vectLOOPGoals;
		vector<unsigned long int> *  vectAFTER_LOOPGoals;
		vector<unsigned long int> *  vectELSEGoals;
		vector<unsigned long int> *  vectEMPTY_ELSEGoals;
		vector<unsigned long int> *  vectCOMPOUNDGoals;
		vector<unsigned long int> *  vectEND_OF_FUNCTIONGoals;
		vector<NonDetCallInfo *> *   vectLineNumberForNonDetCalls;
		
		vector<unsigned long int> *  vctForGoals;
		vector<unsigned long int> *  vctCXXForRangeGoals;
		vector<unsigned long int> *  vctDoWhileGoals;
		vector<unsigned long int> *  vctWhileGoals;
		
		vector<GoalInfo *> *         vectGoalInfo;
		

		unsigned long int counter = 0;
		bool mustGenerateFuncLabelMap = false;
		static GoalCounter& getInstance();
		GoalCounter(GoalCounter const&)    = delete;
		void operator=(GoalCounter const&) = delete;
		//std::string GetNewGoal() = delete;

		std::string GetNewGoalForFuncDecl(clang::FunctionDecl* functionDecl,GoalType goalType);
};
#endif 

