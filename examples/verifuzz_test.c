//#include <assert.h>
//#include <stdlib.h>
//#include <string.h>
//#include <stdarg.h>
//#include <string.h>
//#include <stdio.h>
//#include <unistd.h>


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



extern void __assert_fail (const char *__assertion, const char *__file,
      unsigned int __line, const char *__function);
//void reach_error()
//{ 
	/*assert(0);*/
//}

void reach_error() { ((void) sizeof ((0) ? 1 : 0), __extension__ ({ if (0) ; 
else 
	__assert_fail ("0", "relax-1.c", 91, __extension__ __PRETTY_FUNCTION__);
	//exit(0);
})); }
//int f(){return -1;}
#define BUFF_SIZE 500

#define N_0 (9999 - 9999 + 1 - 1)
#define N_1 (1+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0)
#define N_11 (1+1+1+1+1+1+1+1+1+1+1+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0)
#define N_33 ((1+1+1+N_0+N_0+N_0+N_0+N_0+N_0) * N_11)
#define N_100 (N_33+N_33+N_33+1+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0+N_0)

int main()
{
	/*unsigned long a0 = __VERIFIER_nondet_ulong();
	unsigned long a1 = __VERIFIER_nondet_ulong();
	unsigned long a2 = __VERIFIER_nondet_ulong();
	unsigned long a3 = __VERIFIER_nondet_ulong();
	if(a0 == 66 && a1 == 77 && a2 == 88 && a3 == 99)
		reach_error();
	*/		
	
// testcase must be : 66, 77, 88, 99
	unsigned long arr[4]= {__VERIFIER_nondet_ulong(),__VERIFIER_nondet_ulong(),
			__VERIFIER_nondet_ulong(),__VERIFIER_nondet_ulong()};
	if(
		// all bigger than Zero
		arr[0] > N_0 &&
		arr[1] > N_0 &&
		arr[2] > N_0 &&
		arr[3] > N_0 &&
		
		arr[1] - arr[0] == N_11 &&
		arr[2] - arr[1] == N_11 && 
		arr[3] - arr[2] == N_11 &&	
		arr[3] - arr[0] == N_33 &&
		
			
			
		arr[0] / N_11 == (N_11-(N_1+N_1+N_1+N_1+N_1)) && // sixsix div eleven equal six
			
		// all less than Hundred.Don't write it as Number (^_^)
		arr[0] < N_100 && 
		arr[1] < N_100 && 
		arr[2] < N_100 && 
		arr[3] < N_100)
		reach_error();
	
	 
	 return 0;
}

