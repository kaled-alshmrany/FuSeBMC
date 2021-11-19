#ifndef FUNCCALLINFO_H
#define FUNCCALLINFO_H
#include <string>
#include <vector>

using namespace std;

class FuncCallInfo
{
	public:
		unsigned long int callerID = 0;
		unsigned long int calleeID = 0;
		unsigned long int depth = 0;
		FuncCallInfo(unsigned long int p_callerID, unsigned long int p_calleeID, unsigned long int p_depth);
		
};

class FuncCallList
{
private:
	unsigned long int counter = 0;
	
public:
	vector<FuncCallInfo *> vctFuncCallInfo;
	
	FuncCallList();
	void addFuncCallInfo(unsigned long int p_callerID, unsigned long int p_calleeID, unsigned long int p_depth);
	void print();
	~FuncCallList();
};


#endif /* FUNCCALLINFO_H */

