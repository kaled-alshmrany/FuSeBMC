#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
extern void __VERIFIER_assert(int cond);
extern void __VERIFIER_assume(int cond);
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

//#define assert(x) __VERIFIER_assume(x)
int main()
{
	int a = __VERIFIER_nondet_int();
	int b = __VERIFIER_nondet_int();
	//assert(a > 0 && b > 0); // NOT OK
	//__VERIFIER_assume(a > 0 && b > 0); // OK
	__VERIFIER_assert(a > 0 && b > 0); // NOT OK
	if (a+b == 33)
	{
		GOAL_1:;
		int x = 11;
		return 0;
	}
	if (a+b == 99)
	{
	GOAL_2:;
	int xx = 12;
	}
	exit(0);
	return 1;
}
