
#ifndef MYOPTIONS_H
#define MYOPTIONS_H
#include <string>
#include <map>

using namespace std; 
class MyOptions
{
public:
    std::string inputFile;
    std::string outputFile;
    std::string goalOutputFile;
    std::string goalProFuncOutputDir;
    bool addElse=false;
    bool addGoalAtEndOfFunc=false;
    bool showParseTree=false;
    bool addLabelInFunc=false;
    bool addLabels=false;
    bool addLabelAfterLoop=false;
    //20.05.2020
    // func1 , lbl1
    // func 2, lbl2
    map<string,string> funcLabelMap;
    MyOptions()
    {
        
    }
    string GetLabelForFunc(string func);
};


#endif /* MYOPTIONS_H */

