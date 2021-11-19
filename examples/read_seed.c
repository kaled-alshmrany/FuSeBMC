#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

//gcc -m32 -o read_seed read_seed.c

int main(int argc, char *argv[])
{
	char c = 127;
	long l = c;
	printf("%ld\n",l);
	if (argc != 2)
	{
		printf("%d argument number error\n", argc);
		exit(-1);
	}
	FILE *fptr;
	if ((fptr = fopen(argv[1], "r")) != NULL)
	{
		long lval = 0;
		fread(&lval ,1 , sizeof(long), fptr);
		printf("long=%ld\n", lval);
		int ival = 0;
		fread(&ival ,1 , sizeof(int), fptr);
		printf("int=%d\n", ival);
		
		fread(&ival ,1 , sizeof(int), fptr);
		printf("int=%d\n", ival);
		
		fread(&ival ,1 , sizeof(int), fptr);
		printf("int=%d\n", ival);
	}
	fclose(fptr);
	return 0;
}