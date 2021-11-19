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
void f1(){}
void f2(){}

int main()
{
	int a = __VERIFIER_nondet_int();
	
	int b = __VERIFIER_nondet_int();
	
	int sum = a+ b;
	if(sum == 33)
	{
		char c = __VERIFIER_nondet_char();
		// Do something.
		f1();
	}
	else
	{
		long long ll = __VERIFIER_nondet_longlong();
		// Do something else.
		f2();
	}
	return 0;
}