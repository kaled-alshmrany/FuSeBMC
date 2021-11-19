#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>



int main()
{
	printf(" sizeof(signed char) = %ld\n", sizeof(signed char));
	printf("sizeof(unsigned char) = %ld\n",sizeof(unsigned char));
	printf("sizeof(signed short) = %ld\n",sizeof(signed short));
	printf("sizeof(unsigned short) = %ld\n",sizeof(unsigned short));
	printf("sizeof(signed int) = %ld\n",sizeof(signed int));
	printf("sizeof(unsigned int) = %ld\n",sizeof(unsigned int));
	printf("sizeof(long) = %ld\n",sizeof(long));
	printf("sizeof(unsigned long) = %ld\n",sizeof(unsigned long));
	printf("sizeof(long long) = %ld\n",sizeof(long long));
	printf("sizeof(unsigned long long) = %ld\n",sizeof(unsigned long long));
	printf("sizeof(float) = %ld\n",sizeof(float));
	printf("sizeof(double) = %ld\n",sizeof(double));
	printf("sizeof(_Bool) = %ld\n",sizeof(_Bool));
	
	return 0;
}

