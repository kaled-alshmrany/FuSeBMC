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

extern void __assert_fail(const char *, const char *, unsigned int, const char *);

/*
void fuSeBMC_print_val_in_file_n (char * file_name , char * format, ...)
{
	va_list args;
	va_start (args, format);		
	FILE * fPtr = fopen(file_name, "a");
	if(fPtr == NULL)
	{
	   printf("Error: cannot read file:%s\n" , file_name);
	   return;

	}
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
	
}*/

//void reach_error()
//{ 
	/*assert(0);*/
//}
//int f(){return -1;}
#define BUFF_SIZE 500
int main()
{
	//exit(0);
	//fuSeBMC_print_val_in_file_n("./env.txt","%s\n",getenv("fusebmc_env"));
	//int a1 =  __VERIFIER_nondet_int();
	//const char * a2 = __VERIFIER_nondet_string();
	/*_Bool a3 =__VERIFIER_nondet_bool();
	char a4 = __VERIFIER_nondet_char();
	double a5 = __VERIFIER_nondet_double();
	float a6 = __VERIFIER_nondet_float();
	long a7 =__VERIFIER_nondet_long();
	long long a8 = __VERIFIER_nondet_longlong();
	short a9 = __VERIFIER_nondet_short();
	unsigned char a10 =  __VERIFIER_nondet_uchar();
	unsigned int a11 = __VERIFIER_nondet_uint();
	unsigned long a12 = __VERIFIER_nondet_ulong();
	unsigned long long a13 = __VERIFIER_nondet_ulonglong();
	unsigned short a14 = __VERIFIER_nondet_ushort();*/

	//char * s = __VERIFIER_nondet_string();
	int a =__VERIFIER_nondet_int();
	int b = __VERIFIER_nondet_int();
	int sum = a + b;
	//assert(a != 5);
	if(a > 3)
	{
		__assert_fail("This_IS_FUSEBMC_ASSERTION", "bbb", 1,"func");
		//assert(a==b);
		int zz = 9;
	}
	 
	//if(1)while(1)if(1)for(;;)return 1;
	if(sum == 8);
	if(sum == 9);
	if(a>0 && b>0 && a < 1000 && b <100 && sum == 7)
	{
		//reach_error();
		int z = 99;
		return 10;
	}
	
	else
	
		return   2 - 8 /** ;* //gfgfgfg ;
					 *;** ///   ;   X
					 ;*/ 
				-
				1 ;
	
	return 0;
	
	//return 0;
}

