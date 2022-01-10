// https://www.learn-c.org/en/Linked_lists
// https://www.tutorialspoint.com/data_structures_algorithms/linked_list_program_in_c.htm
#include <goalList.h>
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#ifdef __cplusplus
extern "C" {
#endif

char * fuSeBMC_bitset_arr = NULL;
//FuSeBMC_goal_node_t * fuSeBMC_goal_arr;
//int fuSeBMC_goal_arr_count = 0;
//int fuSeBMC_goal_arr_size = 1024;
int fuSeBMC_env_goals_cnt = 0;
//static int fuSeBMC_bitset_sz_byte = 0;




void fuSeBMC_create_goal_list()
{
	char * goals_count_ptr = alloc_printf("%s_gcnt",fuSeBMC_run_id);
	char * env_goals_count = getenv(goals_count_ptr);
	int goals = 1000;
	if(env_goals_count)
		goals = atoi(env_goals_count);
	
	if(goals<=0)
	{
		fuSeBMC_log_error("goals_count=%d\n",goals);
		//exit(-1);
		goals = 1000;
	}
	//if(goals<1000) goals = 1000;
	fuSeBMC_env_goals_cnt = goals;
	//fuSeBMC_log_error("fuSeBMC_env_goals_cnt=%d\n",fuSeBMC_env_goals_cnt);
	//int bytesNum = fuSeBMC_env_goals_cnt / (CHAR_BIT * sizeof(char));
	//int rest = fuSeBMC_env_goals_cnt % (CHAR_BIT * sizeof(char));
	//if(rest>0) bytesNum += 1;
	//fuSeBMC_bitset_sz_byte = bytesNum;
	//fuSeBMC_bitset_sz_byte += 32 ; // buffer.
	//fuSeBMC_log_error("fuSeBMC_bitset_sz_byte=%d\n",fuSeBMC_bitset_sz_byte);
	if(fuSeBMC_bitset_arr == NULL)
	{
		//fuSeBMC_bitset_arr = fuSeBMC_alloc(fuSeBMC_bitset_sz_byte * sizeof(char));
		//memset(fuSeBMC_bitset_arr,0,fuSeBMC_bitset_sz_byte);
		
		fuSeBMC_bitset_arr = fuSeBMC_alloc((fuSeBMC_env_goals_cnt +1) * sizeof(char));
		memset(fuSeBMC_bitset_arr,0,fuSeBMC_env_goals_cnt+1);
		for(int i=0; i<=fuSeBMC_env_goals_cnt;i++)
			fuSeBMC_bitset_arr[i] = 0;
	}
}

void fuSeBMC_push_in_goal_list(FUSEBMC_goal_t goal)
{
	/*if(goal > (fuSeBMC_bitset_sz_byte * 8))
	{
		fuSeBMC_log_error("goal=%d,bits_size=%u",goal,fuSeBMC_bitset_sz_byte * 8);
		exit(0);
	}*/
	int bytePos = 0;
	char bitPos = 0;
	if(goal != 0)
	{
		bytePos = goal / (sizeof(char) * 8);
		bitPos =  goal %  (sizeof(char) * 8);
	}
	char * tmpPtr = fuSeBMC_bitset_arr + bytePos;
	//fuSeBMC_log_info("BBBBBBB=%s",fuSeBMC_as_bits(&(fuSeBMC_bitset_arr[bytePos]),sizeof(char)));
	*tmpPtr |= (char)1 << bitPos;
}


int fuSeBMC_find_in_goal_list(FUSEBMC_goal_t goal)
{
	int bytePos = 0;
	char bitPos = 0;
	if(goal != 0)
	{
		bytePos = goal / (sizeof(char) * 8);
		bitPos = goal %  (sizeof(char) * 8);
	}
	//char * tmpPtr = fuSeBMC_bitset_arr + bytePos;
	char bit = ((fuSeBMC_bitset_arr)[bytePos] >> bitPos) & (char)1;
	//printf("pos=%d,bit=%d\n",pos, bit);
	//fuSeBMC_log_info("fuSeBMC_isBitSet["FUSEBMC_goal_format"]=%d, bytePos=%d ,bitPos=%d \n",pos,bit,bytePos,bitPos);
	//return bit;
	if(bit == 1) return 1;
	return -1;
}
#ifdef __cplusplus
}
#endif