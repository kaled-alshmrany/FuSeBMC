#ifndef NONDETCALLINFO_H
#define NONDETCALLINFO_H
#include <string>

using namespace std;

class NonDetCallInfo
{
	public:
		unsigned long int line = 0;
		string funcName = "";
		NonDetCallInfo(unsigned long int p_line, string p_funcName);
		
};


#endif /* NONDETCALLINFO_H */

