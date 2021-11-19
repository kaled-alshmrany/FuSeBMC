#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>


extern int __VERIFIER_nondet_int();
extern const char *__VERIFIER_nondet_string();
_Bool __VERIFIER_nondet_bool();
char __VERIFIER_nondet_char();
double __VERIFIER_nondet_double();
float __VERIFIER_nondet_float();
long __VERIFIER_nondet_long();
long long __VERIFIER_nondet_longlong();
short __VERIFIER_nondet_short();
unsigned char __VERIFIER_nondet_uchar();
unsigned int __VERIFIER_nondet_uint();
unsigned long __VERIFIER_nondet_ulong();
unsigned long long __VERIFIER_nondet_ulonglong();
unsigned short __VERIFIER_nondet_ushort();

void f2(int x)
{
	if(x==3)
	{
		printf("x==3\n");
	}
}
void f1(int x)
{
	if(x>0 && x<5)
	{
		printf("x==1\n");
		f2(x);
	}
}


int main()
{
	int x = __VERIFIER_nondet_int();	
	if(x>0 && x<100)
	{
		f1(x);
	}
	return 0;
}