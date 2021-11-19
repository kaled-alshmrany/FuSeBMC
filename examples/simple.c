#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
//gcc -o simple.exe simple.c && ./simple.exe
int main()
{
	unsigned long long x = 8 * 1024;
	unsigned long long r1 = x << 20;
	unsigned long long r2 = x *1024 *1024;
	printf("r1=%llu\n",r1);
	printf("r2=%llu\n",r2);
	return 0;
}