#ifndef STDCFUNCHANDLER_H
#define STDCFUNCHANDLER_H

#include <iostream>
#include <vector>

class StdCFuncHandler
{
public:
	static std::vector<std::string> vctStdCFuncToSearchFor;
	std::vector<std::string> vctStdCFuncFound;
	
	StdCFuncHandler();
	void addIfStdC_Func(std::string pFuncName);
};

#endif /* STDCFUNCHANDLER_H */
