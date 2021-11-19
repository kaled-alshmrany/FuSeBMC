#include <iostream>
#include <FuncCallInfo.h>
#include <MyOptions.h>
using namespace std;
extern MyOptions * myOptions;

FuncCallInfo::FuncCallInfo(unsigned long int p_callerID, unsigned long int p_calleeID, unsigned long int p_depth):
callerID(p_callerID), calleeID(p_calleeID), depth(p_depth)
{
	
}
/********* FuncCallList **********/
FuncCallList::FuncCallList()
{
	
}
void FuncCallList::addFuncCallInfo(unsigned long int p_callerID, unsigned long int p_calleeID, unsigned long int p_depth)
{
	
	for(FuncCallInfo * funcCallInfoPtr : vctFuncCallInfo)
		if(funcCallInfoPtr->callerID == p_callerID &&
				funcCallInfoPtr->calleeID == p_calleeID
				)
		{
			
			if(funcCallInfoPtr->depth >= p_depth)
			{
				funcCallInfoPtr->depth = p_depth;
				
			}
			return;
		}
	FuncCallInfo * funcCallInfo = new FuncCallInfo(p_callerID, p_calleeID,p_depth);
	this->vctFuncCallInfo.push_back(funcCallInfo);
}
void FuncCallList::print()
{
	for(FuncCallInfo * funcCallInfoPtr : vctFuncCallInfo)
	{
		std::cout << funcCallInfoPtr->callerID << " -> " << funcCallInfoPtr->calleeID 
				<<" Depth="<< funcCallInfoPtr->depth<< std::endl;
	}
}
FuncCallList::~FuncCallList()
{
	//if(vctFuncDeclInfo)
	{
		for(FuncCallInfo * funcCallInfoPtr : vctFuncCallInfo)
		{
			delete funcCallInfoPtr;
		}
		vctFuncCallInfo.clear();
	}
}