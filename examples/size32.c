#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>



int main()
{
	printf(" sizeof(signed char) = %d\n", sizeof(signed char));
	printf("sizeof(unsigned char) = %d\n",sizeof(unsigned char));
	printf("sizeof(signed short) = %d\n",sizeof(signed short));
	printf("sizeof(unsigned short) = %d\n",sizeof(unsigned short));
	printf("sizeof(signed int) = %d\n",sizeof(signed int));
	printf("sizeof(unsigned int) = %d\n",sizeof(unsigned int));
	printf("sizeof(long) = %d\n",sizeof(long));
	printf("sizeof(unsigned long) = %d\n",sizeof(unsigned long));
	printf("sizeof(long long) = %d\n",sizeof(long long));
	printf("sizeof(unsigned long long) = %d\n",sizeof(unsigned long long));
	printf("sizeof(float) = %d\n",sizeof(float));
	printf("sizeof(double) = %d\n",sizeof(double));
	printf("sizeof(_Bool) = %d\n",sizeof(_Bool));
	
	return 0;
}

