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
void fuSeBMC_printBits(char * file_name, size_t const size, void const * const ptr)
{
    unsigned char *b = (unsigned char*) ptr;
    unsigned char byte;
    int i, j;
    FILE * fPtr = fopen(file_name, "a");
	if(fPtr == NULL)
	{
	   printf("Error: cannot read file:%s\n" , file_name);
	   return;

	}
	
    for (i = size-1; i >= 0; i--)
	{
        for (j = 7; j >= 0; j--) 
		{
            byte = (b[i] >> j) & 1;
            fprintf (fPtr,"%u", byte);
        }
    }
    fclose(fPtr);
}
#define MAX_INPUT 1000
int main()
{
	//fuSeBMC_print_val_in_file_n("./hosam.txt" ,"%d\n",getpid());
	//__pid_t fuzzer_pid = getppid();
	//if(fuzzer_pid > 0) kill(fuzzer_pid, SIGUSR2);
	char * ptr = malloc(MAX_INPUT * sizeof(char));
	long val = 0;
	int c;
	if ((c = fread(ptr ,sizeof(char),MAX_INPUT , stdin)) > 0) 
	{
		fuSeBMC_print_val_in_file_n("./hosam.txt" ,"\nlength=%d\n",c);
		fuSeBMC_printBits("./hosam.txt", c, ptr);
	}
	else
	{
		fuSeBMC_print_val_in_file_n("./hosam.txt" ,"No input\n");
	}
	return 0;
}

