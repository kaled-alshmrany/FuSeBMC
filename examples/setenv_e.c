#include <stdio.h>
#include <stdlib.h>


int main()
{
	//int x = setenv(const char *envname, const char *envval, int overwrite);
	printf("VAR : %s\n", getenv("xxxxxxx"));
	setenv("xxxxxxx", "yyyyyy",1);
	return 0;
}