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

void reach_error()
{ 
	/*assert(0);*/
}
int f(){return -1;}
#define BUFF_SIZE 500
int main()
{
	int x=0;
	
	if(0)x=0;
	if(0){x=0;}
	while(0)x=0;
	while(0){x=0;}
	for(;;)x=0;
	for(;;){x=0;}
	do{}while(0);
	
	return 0;
}

