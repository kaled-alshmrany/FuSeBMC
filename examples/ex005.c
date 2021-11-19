#include <stdlib.h>
#include <stdio.h>
extern int __VERIFIER_nondet_int();
void f1(){}
void f2(){}
int main()
{
	int a =  __VERIFIER_nondet_int();
	int b = __VERIFIER_nondet_int();
	int sum = a + b;
	if(sum == 33) f1(); else f2();	
	return 0;
}

