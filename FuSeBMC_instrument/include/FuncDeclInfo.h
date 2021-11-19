#ifndef FUNCDECLINFO_H
#define FUNCDECLINFO_H
#include <string>
#include <vector>

using namespace std;

class FuncDeclInfo
{
	public:
		unsigned long int id = 0;
		string funcName = "";
		FuncDeclInfo(unsigned long int p_id, string p_funcName);
		
};

class FuncDeclList
{
private:
	unsigned long int counter = 0;
	
public:
	vector<FuncDeclInfo *> vctFuncDeclInfo;
	
	FuncDeclList();
	unsigned long int addFuncDeclInfo(string p_funcName);
	unsigned long int getFuncDeclID(string p_funcName);
	void print();
	~FuncDeclList();
};
#endif /* FUNCDECLINFO_H */

