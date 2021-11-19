#include <iostream>
#include "FuncDeclInfo.h"
#include <MyOptions.h>
using namespace std;
extern MyOptions * myOptions;

FuncDeclInfo::FuncDeclInfo(unsigned long int p_id, string p_funcName):
			id(p_id), funcName(p_funcName)
{
	
}

/************* FuncDeclList *************/
FuncDeclList::FuncDeclList()
{
	
}
unsigned long int FuncDeclList::addFuncDeclInfo(string p_funcName)
{
	for(FuncDeclInfo * funcDeclInfoPtr : vctFuncDeclInfo)
		if(funcDeclInfoPtr->funcName == p_funcName)
			return funcDeclInfoPtr->id;
	
		
	FuncDeclList::counter ++ ;
	FuncDeclInfo * funcDeclInfo = new FuncDeclInfo(FuncDeclList::counter,p_funcName);
	this->vctFuncDeclInfo.push_back(funcDeclInfo);
	return FuncDeclList::counter;
}
unsigned long int FuncDeclList::getFuncDeclID(string p_funcName)
{
	for(FuncDeclInfo * funcDeclInfoPtr : vctFuncDeclInfo)
		if(funcDeclInfoPtr->funcName == p_funcName)
			return funcDeclInfoPtr->id;
	return 0;	
}
void FuncDeclList::print()
{
	for(FuncDeclInfo * funcDeclInfoPtr : vctFuncDeclInfo)
	{
		std::cout << funcDeclInfoPtr->id << ":" << funcDeclInfoPtr->funcName << std::endl;
	}
	
}

FuncDeclList::~FuncDeclList()
{
	//if(vctFuncDeclInfo)
	{
		for(FuncDeclInfo * funcDeclInfoPtr : vctFuncDeclInfo)
		{
			delete funcDeclInfoPtr;
		}
		vctFuncDeclInfo.clear();
	}
}
