#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

//rm -f ./goals_c.xml && gcc -o append_to_end.exe append_to_end.c && ./append_to_end.exe&& cat ./goals_c.xml
unsigned int fuSeBMC_category = 2 ;
char * fuSeBMC_run_id = "kwMZsjuCfgcHvgnceEnOiuAKr";
int IsFirstRun = 1;
void fuseGoalCalled(unsigned long int goal)
{
			
	FILE * fPtr;
	if(IsFirstRun == 1)
	{
		 fPtr = fopen("./goals_c.xml", "w+b");
		 if(fPtr == NULL)
		 {
			 printf("Error: cannot read file:%s\n" , "./goals_c.txt");
			 return;
		 }
		fprintf(fPtr,"<testcase>\n");
		fprintf(fPtr,"<input>%lu</input>\n",goal);
		fprintf(fPtr,"</testcase>");
		IsFirstRun = 0;
	}
	else
	{
		 fPtr = fopen("./goals_c.xml", "r+b");
		 if(fPtr == NULL)
		 {
			 printf("Error: cannot read file:%s\n" , "./goals_c.txt");
			 return;
		 }
		int fseek_res = fseek(fPtr, -11, SEEK_END);
		printf("res=%d\n", fseek_res);
		fprintf(fPtr,"<input>%lu</input>\n",goal);
		fprintf(fPtr,"</testcase>");		
	}
	fclose(fPtr);
}
int main()
{
	fuseGoalCalled(1);
	fuseGoalCalled(2);
	fuseGoalCalled(3);
	fuseGoalCalled(4);
	fuseGoalCalled(5);
	return 0;
}