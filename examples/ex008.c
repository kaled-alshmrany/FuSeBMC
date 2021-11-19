#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>


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
void f(){}

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
	
}

int main()
{
	/*if(strcmp (getenv("id"),"yyy.xml") == 0)
	{
		fuSeBMC_print_val_in_file_n("./hosam.txt" ,"%s\n",getenv("id"));
	}
	else 
		fuSeBMC_print_val_in_file_n("./hosam.txt" ,"%s\n","NOOOOOO");
	 */
	
	int x1 =__VERIFIER_nondet_int();
	int x2 =__VERIFIER_nondet_int();
	//kill(getppid(), SIGUSR2);
	
	if(x1 == 10)
	{
		
	}
	if(x2 == 10)
	{
		
	}
	if(x1 == 100)
	{
		
	}
	if(x2 == 100)
	{
		
	}
	if(x1 + x2  == 100)	
	{
		int x3 =__VERIFIER_nondet_int();
		int x4 =__VERIFIER_nondet_int();
		if(x3 + x4 == 100) return 0;
	}
	return 0;
}

