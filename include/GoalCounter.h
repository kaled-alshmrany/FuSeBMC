#ifndef GOALCOUNTER_H
#define GOALCOUNTER_H

#include <map>
#include <string>
#include <vector>
using namespace std; 
class GoalCounter
{

    private:
        static GoalCounter    instance;  
        GoalCounter();        
        
    public:
        map<string,vector<string>> *funcLabelMap;
        unsigned long long counter = 0;
        bool mustGenerateFuncLabelMap = false;
        static GoalCounter& getInstance();
        GoalCounter(GoalCounter const&)     = delete;
        void operator=(GoalCounter const&)  = delete;
        //std::string GetNewGoal() = delete;
        std::string GetNewGoalForFunc(std::string func);
};

#endif 

