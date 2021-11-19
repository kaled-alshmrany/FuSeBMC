#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include <sys/shm.h>
//#include <errno.h>
#include <limits.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <sys/time.h>

#include <stdbool.h>
#include <config.h>
#include <FuSeBMC_TCGen.h>
#include <inputList.h>
#include <inputTypes.h>

#ifdef __cplusplus
extern "C" {
#endif

// 1 for error-call
// 2 cover-branches
extern unsigned int fuSeBMC_category;
extern char * fuSeBMC_run_id;


//must be >= 0; you can use RAND_MAX
#define FUSEBMC_MIN_RANDOM 0
#define FUSEBMC_MAX_RANDOM 0

#define FUSEBMC_MAX_STRING_SIZE 100
#define FUSEBMC_MIN_STRING_SIZE 1
#define FUSEBMC_TESTCASE_FILENAME_ERROR_CALL "./test-suite/FuSeBMC_Fuzzer_testcase.xml"

#define FUSEBMC_SHARED_MEM_SIZE 2048
//static rlim_t mem_limit = 5 * 1024; // 8 GIGA

// 12 seconds
#define FUSEBMC_COVERBRANCHES_TIMEOUT (__time_t) 12 
#define FUSEBMC_ERRORCALL_TIMEOUT (__time_t) 120

#define alloc_printf(_str...)({\
	char * _tmp;\
	int32_t _len = snprintf(NULL, 0, _str);\
	if (_len < 0) {fuSeBMC_log_error("Whoa, snprintf() fails?!");exit(0);}\
	_tmp = malloc(_len + 1);\
	snprintf((char*)_tmp, _len + 1, _str);\
	_tmp;\
	})

#define FUSEBMC_random_number_signed()({\
	if(!fuSeBMC_IsRandomHasSeed)\
		{\
			srand(getpid());\
			fuSeBMC_IsRandomHasSeed = 1;\
		}\
		char rnd_input = FUSEBMC_MAX_RANDOM;\
		if (FUSEBMC_MAX_RANDOM != FUSEBMC_MIN_RANDOM)\
		rnd_input = (rand() %\
				(FUSEBMC_MAX_RANDOM - FUSEBMC_MIN_RANDOM + 1)) + FUSEBMC_MIN_RANDOM;\
		if(rand() % 2 == 0) rnd_input *= -1;\
		rnd_input;\
})
#define FUSEBMC_random_number_unsigned()({\
	if(!fuSeBMC_IsRandomHasSeed)\
		{\
			srand(getpid());\
			fuSeBMC_IsRandomHasSeed = 1;\
		}\
		char rnd_input = FUSEBMC_MAX_RANDOM;\
		if (FUSEBMC_MAX_RANDOM != FUSEBMC_MIN_RANDOM)\
		rnd_input = (rand() %\
				(FUSEBMC_MAX_RANDOM - FUSEBMC_MIN_RANDOM + 1)) + FUSEBMC_MIN_RANDOM;\
		rnd_input;\
})

pthread_mutex_t * fuSeBMC_lock = NULL;
unsigned char fuSeBMC_IsNewGoalsAdded = 0;
unsigned char fuSeBMC_IsRandomHasSeed = 0;
unsigned char fuSeBMC_IsFirstElementInTestcase = 1;
static char outFileName[100];// for Testcase and covered goals.
char * fuSeBMC_test_case_file = NULL;
char * fuSeBMC_goal_covered_by_this_testcase_file = NULL;
int fuSeBMC_shm_id = -1;
int fuSeBMC_shm_input_size_id = -1;
unsigned char fuSeBMC_IsStdInCopied = 0;

//void * fuSeBMC_stdin = NULL;
//void * fuSeBMC_stdin_curr = NULL;
//unsigned int fuSeBMC_stdin_len = 0 , fuSeBMC_stdin_consumed = 0;

//unsigned int * fuSeBMC_input_size_ptr = NULL;

char * fuSeBMC_bitset_arr = NULL;
int fuSeBMC_env_goals_cnt = 0;
//FUSEBMC_goal_t fuSeBMC_bitset_sz_byte = 0;


FUSEBMC_goal_t last_goal= 0;


//extern FuSeBMC_input_node_t * fuSeBMC_input_arr;
//extern int fuSeBMC_input_arr_count;

/*Helper to print values in file.
 * USAGE: fuSeBMC_print_val_in_file("file1.txt","%s%d", "Hello" , 10);
 */
void fuSeBMC_print_val_in_file (char * file_name , char * format, ...)
{
	FILE * fPtr = fopen(file_name, "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot read file:%s\n" , file_name);
		return;
	}
	va_list args;
	va_start (args, format);
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}

void fuSeBMC_log_error (char * format, ...)
{
	//return;
	FILE * fPtr = fopen("./TCGen_error.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot write file:%s\n" , "./TCGen_error.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	fprintf (fPtr, "\n++++++++++++++++++++++++++\npid=%d\n",getpid());
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}
void fuSeBMC_log_info (char * format, ...)
{
	//return;
	FILE * fPtr = fopen("./TCGen_info.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot write file:%s\n" , "./TCGen_info.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	fprintf (fPtr, "\n++++++++++++++++++++++++++\npid=%d\n",getpid());
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}
char * fuSeBMC_as_bits(void const * const ptr,size_t const size)
{
	int bit_char_size = size * 8 + 1;
	char * bit_char = malloc(bit_char_size);
	char * bit_char_tmp = bit_char;
	memset(bit_char,'\0',bit_char_size);
	char *b = (char*) ptr;
	//unsigned char byte;
	//int i;
	
	for(size_t i=0; i< size;i++)
	{
		char byte = *b;
		sprintf(bit_char_tmp,"%c%c%c%c%c%c%c%c",
				(byte & 0x01 ? '1' : '0'),
				(byte & 0x02 ? '1' : '0'),
				(byte & 0x04 ? '1' : '0'),
				(byte & 0x08 ? '1' : '0'),
				(byte & 0x10 ? '1' : '0'),
				(byte & 0x20 ? '1' : '0'),
				(byte & 0x40 ? '1' : '0'), // 64 = 1000000
				(byte & 0x80 ? '1' : '0') // 128 =10000000
				 );
		b++;
		bit_char_tmp += 8;
	}
	
	/*for (i = size-1; i >= 0; i--)
	{
		for (j = 7; j >= 0; j--) 
		{
			byte = (b[i] >> j) & 1;
		sprintf (bit_char_tmp,"%u", byte);
			bit_char_tmp ++;
		}
	}*/
	return bit_char;
}
#ifdef STAND_ALONE
void fuSeBMC_setup_shm(void)
{
	fuSeBMC_env_goals_cnt = 1000;
	fuSeBMC_bitset_arr = malloc((fuSeBMC_env_goals_cnt+1) * sizeof(char));
	for(int i=0; i<=fuSeBMC_env_goals_cnt;i++)
		fuSeBMC_bitset_arr[i] = 0;
	fuSeBMC_input_size_ptr = malloc(sizeof(unsigned int));
	*fuSeBMC_input_size_ptr = 0;
}
#else
void fuSeBMC_setup_shm(void)
{
#ifdef FUSEBMC_USE_BITSET
	if(fuSeBMC_category == 2 )
	{
		if(fuSeBMC_bitset_arr == NULL)
		{
			key_t some_key = ftok(".", 'x');
			char * goals_count_ptr = alloc_printf("%s_gcnt",fuSeBMC_run_id);
			char * env_goals_count = getenv(goals_count_ptr);
			int goals = 1000;
			if(env_goals_count)
				goals = atoi(env_goals_count);

			if(goals<=0)
			{
				fuSeBMC_log_error("goals_count=%d",goals);
				exit(-1);
			}
			else 
				fuSeBMC_env_goals_cnt = goals;

			//fuSeBMC_log_info("fuSeBMC_env_goals_cnt=%d",fuSeBMC_env_goals_cnt);
			//free(goals_count_ptr);
			//free(env_goals_count);
			//fuSeBMC_log_info("fuSeBMC_env_goals_cnt=%d",fuSeBMC_env_goals_cnt);
			//int bytesNum = goals / (CHAR_BIT * sizeof(char));
			//int rest = goals % (CHAR_BIT * sizeof(char));
			//if(rest>0) bytesNum += 1;
			//fuSeBMC_bitset_sz_byte = bytesNum;
			//fuSeBMC_shm_id = shmget(some_key, (fuSeBMC_bitset_sz_byte + 1) * sizeof(char), 0666);
			fuSeBMC_shm_id = shmget(some_key, (fuSeBMC_env_goals_cnt+1) * sizeof(char), 0666);
			if (fuSeBMC_shm_id < 0)
			{
				fuSeBMC_log_error("fuSeBMC_setup_shm() failed\n");
				exit(0);
			}
			fuSeBMC_bitset_arr = shmat(fuSeBMC_shm_id, NULL, 0);
			if (fuSeBMC_bitset_arr == (void *)-1)
			{
				fuSeBMC_log_error("shmat() failed\n");
				exit(0);
			}
		}
	}
	//CoverBranches and ErrorCall
	/*if(fuSeBMC_input_size_ptr == NULL)
	{
		key_t key_for_input_size = ftok("./seeds/", 'x');
		//fuSeBMC_log_info("key_for_input_size=%d\n",key_for_input_size);
		fuSeBMC_shm_input_size_id = shmget(key_for_input_size,sizeof(unsigned int), 0666);
		if (fuSeBMC_shm_input_size_id < 0)
		{
			fuSeBMC_log_error("fuSeBMC_setup_shm() 'fuSeBMC_shm_input_size_id' failed\n");
			exit(0);
		}

		fuSeBMC_input_size_ptr = shmat(fuSeBMC_shm_input_size_id, NULL, 0);
		if (fuSeBMC_input_size_ptr == (unsigned int *)-1)
		{
			fuSeBMC_log_error("shmat() 'fuSeBMC_shm_input_size_id' failed\n");
			exit(0);
		}
		else
			*fuSeBMC_input_size_ptr = 0;
	}*/
#else
	
	//int * tmpPtr = fuSeBMC_run_id;
	//fuSeBMC_shm_id = shmget(IPC_PRIVATE, FUSEBMC_SHARED_MEM_SIZE * sizeof(unsigned int), IPC_CREAT | IPC_EXCL | 0600);
	
	fuSeBMC_shm_id = shmget(some_key, FUSEBMC_SHARED_MEM_SIZE * sizeof(FUSEBMC_goal_t),  0666);
	if (fuSeBMC_shm_id < 0)
	{
		fuSeBMC_log_error("fuSeBMC_setup_shm() failed");
		exit(0);
	}
	fuSeBMC_goals_covered_arr = shmat(fuSeBMC_shm_id, NULL, 0);
	if (fuSeBMC_goals_covered_arr == (void *)-1)
	{
		fuSeBMC_log_error("shmat() failed");
		exit(0);
	}
	//memset(fuSeBMC_goals_covered_arr, (unsigned int)0, FUSEBMC_SHARED_MEM_SIZE);
	//for(int i=0; i < FUSEBMC_SHARED_MEM_SIZE; i++)
	//	fuSeBMC_log_info("fuSeBMC_goals_covered_arr[%d]=%u\n",i, fuSeBMC_goals_covered_arr[i]);
	
	for(int i=0; i < FUSEBMC_SHARED_MEM_SIZE; i++)
		if(fuSeBMC_goals_covered_arr[i] == 0)
		{
			fuSeBMC_goals_covered_arr_count = i+1;
			break;
		}
#endif

}
#endif //STAND_ALONE
void fuSeBMC_init()
{
	fuSeBMC_init_mutex();
	//if(fuSeBMC_IsStdInCopied == 0) fuSeBMC_copy_stdin();
}
void fuSeBMC_init_mutex()
{
	if(fuSeBMC_lock == NULL)
	{
		fuSeBMC_lock = malloc(sizeof(pthread_mutex_t));
		if (pthread_mutex_init(fuSeBMC_lock, NULL) != 0)
		{
			printf("\n--------------------\n mutex init failed\n");
			fuSeBMC_log_error("mutex init failed\n");
			exit(0);
		}
		else
		{
			//fuSeBMC_log_info("fuSeBMC_init_mutex Done\n");
			fuSeBMC_setup_signal_handlers();
			
			//struct rlimit r;
			//if (mem_limit)
			//{
			//r.rlim_max = r.rlim_cur = (rlim_t)(mem_limit << 20);// 1024 * 1024
//#ifdef RLIMIT_AS
//			setrlimit(RLIMIT_AS, &r);
//#else
//			setrlimit(RLIMIT_DATA, &r);
//#endif
			//}
			//r.rlim_max = r.rlim_cur = 0; // core dump
			//setrlimit(RLIMIT_CORE, &r);
			
			fuSeBMC_setup_shm();
			
		}
		// Error-call
		if(fuSeBMC_category == 1 )
		{
			if(buckets_arr == NULL)
				fuSeBMC_create_input_list();
		}
		else
		// cover-branches
		if(fuSeBMC_category == 2 )
		{
			//if(fuSeBMC_IsPrevTotalCoveredGoalsLoaded != 1)
			//	fuSeBMC_readPrevTotalCoveredGoals();
			//if(fuSeBMC_bitset_arr == NULL || fuSeBMC_input_size_ptr == NULL)
			//	fuSeBMC_setup_shm();

			if(buckets_arr == NULL)
				fuSeBMC_create_input_list();
		}
	}
}


char fuSeBMC_generate_random_number_signed()
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	if (FUSEBMC_MAX_RANDOM == FUSEBMC_MIN_RANDOM) return FUSEBMC_MAX_RANDOM;
	//int rnd_input = rand();
	char rnd_input = (rand() %
			(FUSEBMC_MAX_RANDOM - FUSEBMC_MIN_RANDOM + 1)) + FUSEBMC_MIN_RANDOM;
	if(rand() % 2 == 0) rnd_input *= -1;
	//fuSeBMC_log_input("%d\n", (int)rnd_input);
	return rnd_input;
}
char fuSeBMC_generate_random_number_unsigned()
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	if (FUSEBMC_MAX_RANDOM == FUSEBMC_MIN_RANDOM) return FUSEBMC_MAX_RANDOM;
	//int rnd_input = rand();
	int rnd_input = (rand() %
			(FUSEBMC_MAX_RANDOM - FUSEBMC_MIN_RANDOM + 1)) + FUSEBMC_MIN_RANDOM;
	
	//fuSeBMC_log_input("%d\n", (int)rnd_input);
	return rnd_input;
}
/**function to convert ascii char[] to hex-string (char[])
 *Example "AB" = 0x4142s
 */

char * fuSeBMC_string2hexString(char* input)
{
	int dest_len = (strlen(input)*2)+1+2 ;//*2: ech char converted to 2 chars; +1 for \n ; +2 for 0x
	char* output = malloc(dest_len * sizeof(char));
	memset(output,'\0',dest_len);
	//printf("dest_len=%d\n",dest_len);
	int loop = 0;
	int i = 0;
	sprintf(output,"%s", "0x");
	char* tmp_ptr = output;
	tmp_ptr += 2;
	while(input[loop] != '\0')
	{
		tmp_ptr += i;
		sprintf(tmp_ptr,"%02X", input[loop]);
		loop += 1;
		i += 2;
	}
	//insert NULL at the end of the output string
	tmp_ptr[i++] = '\0';
	return output;
}
/**
 * returns a random text with a given length.
 * @param length : the required length of the random text.
 * @return 
 */
char * fuSeBMC_generate_random_text(int length)
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	const char alphanum[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuv";
	int stringLength = sizeof(alphanum) - 1;
	char * rnd_text = malloc(sizeof(char) * length + 1); // +1 for '\0'
	char * tmp_ptr = rnd_text;
	//memset(rnd_text, '\0',length);
	for(int i = 0; i < length; ++i)
	{
		*tmp_ptr = alphanum[rand() % stringLength];
		tmp_ptr++;
	}
	*tmp_ptr = '\0';
	return rnd_text;
}

void fuSeBMC_Write_InputList_in_Testcase_CoverBranches()
{
	//if(fuSeBMC_input_arr_count == 0) return; // No Inputs
	FILE *fptr;
	if(fuSeBMC_IsFirstElementInTestcase == 1)
	{
		char * tmp_random_str;
		while(1)
		{
			memset(outFileName,'\0',100);
			tmp_random_str = fuSeBMC_generate_random_text(20);
			snprintf(outFileName, 100, "./test-suite/FUZ_%s_" FUSEBMC_goal_format ".xml", tmp_random_str,last_goal);
			free(tmp_random_str);
			if(access(outFileName, F_OK ) == 0 )
			{
				// file exists
			}
			else break;
		}
		fptr = fopen(outFileName, "w+b");
		if(fptr == NULL)
		{
			printf("Error: cannot write file:%s\n", outFileName);
			fuSeBMC_log_error("Error: cannot write file:%s\n", outFileName);
			return;
		}
		
		fprintf(fptr,"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n");
		fprintf(fptr,"<!DOCTYPE testcase PUBLIC \"+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN\" \"https://sosy-lab.org/test-format/testcase-1.0.dtd\">\n");
		fprintf(fptr,"<testcase>\n");
		fuSeBMC_Write_InputList_in_FD(fptr);
		//fprintf(fptr,"<!--last_goal=" FUSEBMC_goal_format  "-->\n",last_goal);
		//fprintf(fptr,"<!--pid=%d-->\n",getpid());
		fprintf(fptr,"</testcase>");
		fuSeBMC_IsFirstElementInTestcase = 0;
		//fuSeBMC_log_info("Add New in %s\n",outFileName);
	}
	else 
	{
		//fuSeBMC_IsFirstElementInTestcase = 0;
		fptr = fopen(outFileName, "r+b");
		if(fptr == NULL)
		{
			printf("Error: cannot write file:%s\n", outFileName);
			fuSeBMC_log_error("Error: cannot write file:%s\n", outFileName);
			return;
		}
		int seek_res = fseek(fptr, -11, SEEK_END);
		if(seek_res != 0)
			fuSeBMC_log_error("seek_res = %d\n",seek_res);
		fuSeBMC_Write_InputList_in_FD(fptr);
		//fprintf(fptr,"<!--last_goal=" FUSEBMC_goal_format "-->\n",last_goal);
		//fprintf(fptr,"<!--pid=%d-->\n",getpid());
		fprintf(fptr,"</testcase>");
		//int inputs_count = fuSeBMC_count_input_list(fuSeBMC_input_list_head);
		//fuSeBMC_log_info("Add Not in %s, inpCount = %d\n", outFileName, inputs_count);
	}
	fclose(fptr);
	
}
void fuSeBMC_Write_InputList_in_Testcase_ErrorCall()
{
	
	//if(fuSeBMC_input_list_head == NULL) return; // No saved Inputs.
	//fuSeBMC_reverse_input_list(&fuSeBMC_input_list_head);
	if(access(FUSEBMC_TESTCASE_FILENAME_ERROR_CALL, F_OK) == 0)
	{
		// file exists
		exit(0);
	}
	FILE *fptr;
	fptr = fopen(FUSEBMC_TESTCASE_FILENAME_ERROR_CALL, "w+b");
	if(fptr == NULL)
	{
		printf("Error: cannot write file:%s\n",FUSEBMC_TESTCASE_FILENAME_ERROR_CALL);
		fuSeBMC_log_error("Error: cannot write file:%s\n",FUSEBMC_TESTCASE_FILENAME_ERROR_CALL);
		return;
	}
	fprintf(fptr,"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n");
	fprintf(fptr,"<!DOCTYPE testcase PUBLIC \"+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN\" \"https://sosy-lab.org/test-format/testcase-1.0.dtd\">\n");
	fprintf(fptr,"<testcase>\n");
	fuSeBMC_Write_InputList_in_FD(fptr);
	fprintf(fptr,"</testcase>");
	fclose(fptr);
}

void fuSeBMC_Write_InputList_in_FD(FILE * fptr)
{
	//fuSeBMC_log_error("fuSeBMC_input_arr_count=%d",fuSeBMC_input_arr_count);
	//if(fuSeBMC_input_arr == NULL ) fuSeBMC_log_error("array is NULL");
	//if(fuSeBMC_input_arr_count == 0) return;
	//for(int i=0; i< fuSeBMC_input_arr_count;i++)
	//fuSeBMC_log_info("bucket_idx=%d\n",bucket_idx);
	for(int b = 0; b <= bucket_idx; b++)
	{
		int idx = (b==bucket_idx)?elem_idx : ELEMENTS_PER_BUCKET - 1;
		for(int e=0; e<=idx; e++)
	{
		FuSeBMC_input_node_t * current = &(buckets_arr[b][e]);
		
		if(current->input_type == _char)
		{
			fprintf(fptr,"<input type=\"char\">"); 
#ifdef FUSEBMC_EXPORT_AS_BITS
			char * bits_ptr = fuSeBMC_as_bits(fuSeBMC_input_arr[i].val_ptr,
					fuSeBMC_get_sizeof_inputType(fuSeBMC_input_arr[i].input_type));
			fprintf(fptr,"%s",bits_ptr);
			free(bits_ptr);
#else
			fprintf(fptr,"%hhd",*((char *)current->val_ptr)); // this is.
#endif
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _uchar)
		{
			fprintf(fptr,"<input type=\"unsigned char\">");
			//unsigned int val = (unsigned int)(unsigned char)(*((unsigned char *)current->val_ptr));
			fprintf(fptr,"%hhu",*((unsigned char *)current->val_ptr));
			//fprintf(fptr,"%u",*((unsigned char *)current->val_ptr));
			
			//fprintf(fptr,"%u",val);
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _short)
		{
			fprintf(fptr,"<input type=\"short\">");
			fprintf(fptr,"%hd",*((short *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _ushort)
		{
			fprintf(fptr,"<input type=\"unsigned short\">");
			fprintf(fptr,"%hu",*((unsigned short *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _int)
		{
			fprintf(fptr,"<input type=\"int\">");
#ifdef FUSEBMC_EXPORT_AS_BITS
			char * bits_ptr = fuSeBMC_as_bits(fuSeBMC_input_arr[i].val_ptr,fuSeBMC_get_sizeof_inputType(fuSeBMC_input_arr[i].input_type));
			fprintf(fptr,"%s",bits_ptr);
			free(bits_ptr);
#else
			//int val = (int)(*((int *)current->val_ptr));
			fprintf(fptr,"%d",*((int *)current->val_ptr));
#endif
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _uint) 
		{
			fprintf(fptr,"<input type=\"unsigned int\">");
			fprintf(fptr,"%u",*((unsigned int *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _long)
		{
			fprintf(fptr,"<input type=\"long\">");
			fprintf(fptr,"%ld",*((long*)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _ulong) 
		{
			fprintf(fptr,"<input type=\"unsigned long\">");
			fprintf(fptr,"%lu",*((unsigned long *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _longlong ) 
		{
			fprintf(fptr,"<input type=\"long long\">");
			fprintf(fptr,"%lld",*((long long *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _ulonglong ) 
		{
			fprintf(fptr,"<input type=\"unsigned long long\">");
			fprintf(fptr,"%llu",*((unsigned long long *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _float ) 
		{
			fprintf(fptr,"<input type=\"float\">");
			//fprintf(fptr,"%f",*((float *)fuSeBMC_input_arr[i].val_ptr));
			fprintf(fptr,"%.18e",*((float *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _double) 
		{
			fprintf(fptr,"<input type=\"double\">");
			fprintf(fptr,"%.18e",*((double *)current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _bool)
		{
			fprintf(fptr,"<input type=\"_Bool\">");
			/*char ct = (char)*((char *)fuSeBMC_input_arr[i].val_ptr);
			if(ct != 0 && ct != 1)
			{
				fuSeBMC_log_error("bool is %hhd\n",ct);
				fprintf(fptr,"<!--bool is %hhd-->\n",ct);
				_Bool bl = (_Bool)*((_Bool *)fuSeBMC_input_arr[i].val_ptr);
				if(bl == true)
					fprintf(fptr,"<!--value_true-->\n");
				else
					fprintf(fptr,"<!--value_false-->\n");
			}*/
#ifdef FUSEBMC_EXPORT_AS_BITS
			char * bits_ptr = fuSeBMC_as_bits(fuSeBMC_input_arr[i].val_ptr,
					fuSeBMC_get_sizeof_inputType(fuSeBMC_input_arr[i].input_type));
			fprintf(fptr,"%s",bits_ptr);
			free(bits_ptr);
#else
			//_Bool val = (_Bool)*((_Bool *)current->val_ptr);
			//(val == true)?fprintf(fptr,"1"):fprintf(fptr,"0");
			fprintf(fptr,"%hhd", *((_Bool *)current->val_ptr));
#endif
			fprintf(fptr,"</input>\n");
		}
		else if(current->input_type == _string)
		{ 
			fprintf(fptr,"<input type=\"string\">"); // No derefrence.
			//fprintf(fptr,"%s",((char *)current->val_ptr));
			fprintf(fptr,"%s",fuSeBMC_string2hexString(current->val_ptr));
			fprintf(fptr,"</input>\n");
		}
	}// End FOR
	}
}

void fuSeBMC_reach_error()
{
	//Reach-Error
	if(fuSeBMC_category == 1)
	{
		char * fuzzer_id_ptr = alloc_printf("%s_fuzid",fuSeBMC_run_id);
		char * fuzzer_id_str = getenv(fuzzer_id_ptr);
		__pid_t fuzzer_id = 0;
		if(fuzzer_id_str)
			fuzzer_id = (__pid_t)atol(fuzzer_id_str);

		if(fuzzer_id<=0)
		{
			//fuSeBMC_log_info("Nfuzzer_id=%ld",fuzzer_id);
			//exit(-1);
			fuzzer_id = getppid();
		}
		//fuSeBMC_log_info("fuzzer_id=%ld",fuzzer_id);
		
		fuSeBMC_print_val_in_file("./fuSeBMC_reach_error_tcgen.txt","%s\n","fuSeBMC_reach_error_from_TCGen");
		fuSeBMC_Write_InputList_in_Testcase_ErrorCall();
		if(access(FUSEBMC_TESTCASE_FILENAME_ERROR_CALL, F_OK) == 0 )
		{
			// file exists
			/*char zip_command[1024];
			memset(zip_command,'\0',1024);
			snprintf(zip_command, 1024, "zip -j ./test-suite.zip %s", FUSEBMC_TESTCASE_FILENAME_ERROR_CALL); // -j Junk path; don't add path.
			system(zip_command);*/
		}
		
		//kill(getppid(), SIGINT);
		//kill(getppid(), SIGUSR2);
		
		if(fuzzer_id > 1)
			kill(fuzzer_id, SIGTERM);
	}
}
// will inserted after return in main method.
void fuSeBMC_return(int code)
{
	//fuSeBMC_print_val_in_file("./fuSeBMC_return.txt", "code=%d\n" , code);
	fuSeBMC_exit(code);
}
void fuSeBMC_exit(int code)
{
	//fuSeBMC_print_val_in_file("./exit.txt", "code=%d\n" , code);
	//if(fuSeBMC_input_arr_count == 0) return; // No saved Inputs.
	
	//cover-branches
	if(fuSeBMC_category == 2)
	{
		/*if(fuSeBMC_IsNewGoalsAdded == 0) return; // No new goals are covered.
		char outFileName[100];// for Testcase and covered goals.
		char * tmp_random_str;
		while(1)
		{
			memset(outFileName,'\0',100);
			tmp_random_str = fuSeBMC_generate_random_text(30);
			snprintf(outFileName, 100, "./test-suite/FUZ_%s.xml", tmp_random_str);
			if(access(outFileName, F_OK ) == 0 )
			{
				// file exists
				free(tmp_random_str);
			}
			else break;
		}
		*/
		//1- write the testcase.
		//fuSeBMC_Write_InputList_in_Testcase(outFileName);
		
		// Append To Zip Archive.
		/*if(access(outFileName, F_OK) == 0 )
		{
			// file exists
			char zip_command[1024];
			memset(zip_command,'\0',1024);
			snprintf(zip_command, 1024, "zip -j ./test-suite.zip %s", outFileName); // -j Junk path; don't add path.
			system(zip_command);
		}*/

		//2- Write covered goals by this input.
		/*memset(outFileName,'\0',100);
		snprintf(outFileName, 100, "./test-suite/%s.txt", tmp_random_str);
		FILE * fptr = fopen(outFileName,"w");
		if(fptr == NULL)
		{
		   printf("Error: cannot write to file:%s!\n", outFileName); 
	#ifdef MYDEBUG
		   exit(1);
	#endif
		}
		pthread_mutex_lock(fuSeBMC_lock);
		FuSeBMC_node_t * current = fuSeBMC_list_head;
		while (current != NULL)
		{
			fprintf(fptr,"%lu\n", current->val);
			current = current->next;
		}
		fclose(fptr);
		*/
		//free(tmp_random_str);
		
		//3- Save the Covered goals in file.
		/*if(fuSeBMC_IsNewGoalsAdded == 1)
		{
			FILE *fptr;
			fptr = fopen("./FuSeBMC_Fuzzer_goals_covered.txt","a");
			if(fptr == NULL)
			{
				printf("Error: cannot write to file:./FuSeBMC_Fuzzer_goals_covered.txt!");
				fuSeBMC_log_error("Error: cannot write to file:./FuSeBMC_Fuzzer_goals_covered.txt");
				pthread_mutex_unlock(fuSeBMC_lock);
				return;
			}
			FuSeBMC_goal_node_t * current = fuSeBMC_goal_list_head;
			while (current != NULL)
			{
				if(current->is_new == '0') break;
				fprintf(fptr,"%lu\n", current->val);
				current = current->next;
			}
			*/
			//fclose(fptr);
		}
		
		
		//3 - Save the covered goals in Environment.
		
		/*const int env_var_size = 1024; // 512 MB
		char * buffer = malloc(env_var_size * sizeof(char));
		memset(buffer, '\0' , env_var_size);
		
		FuSeBMC_node_t * current = fuSeBMC_list_head;
		while (current != NULL)
		{
			sprintf(buffer, "%lu",current->val);
			current = current->next;
			if(current != NULL)
				sprintf(buffer, "|");
		}
		int res = setenv(fuSeBMC_run_id, buffer, 1);  // 1: overwrite the old value.
		fuSeBMC_print_val_in_file("./buffer.txt","buffer=%s\n", buffer);
		*/
		//pthread_mutex_unlock(fuSeBMC_lock);

		
		//Must Exit.
		exit(code);
	}

void fuSeBMC_abort_prog()
{
	//cover-branches
	//if(fuSeBMC_category == 2)
	{
		//fuSeBMC_exit(0);
		//abort();
		//exit(0);
	}
	
	// code here
	//abort();
	exit(0);
}
void fuSeBMC___assert_fail (const char *__assertion, const char *__file,
				unsigned int __line, const char *__function)
{
	//cover-branches
	if(fuSeBMC_category == 2)
	{
		//fuSeBMC_exit(0);
	}
}
void __VERIFIER_assume(int cond)
{
	//cover-branches
	/*if(fuSeBMC_category == 2)
	{
		return;
	}*/

	if(!cond)
	{
		//fuSeBMC_abort_prog();
		exit(0);
	}
}

void __VERIFIER_error()
{
	// You can Implement it to check if '__VERIFIER_error()' is called.
	exit(0);

}

char __VERIFIER_nondet_char()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	int c;
	char * val_ptr = fuSeBMC_push_in_input_list(_char,NULL,sizeof(char));
	if ((c = fread(val_ptr ,1 , sizeof(char), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}


unsigned char __VERIFIER_nondet_uchar()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(unsigned char);
	//unsigned char val = 0;
	int c;
	unsigned char * val_ptr = fuSeBMC_push_in_input_list(_uchar,NULL,sizeof(unsigned char));
	if ((c = fread(val_ptr ,1 , sizeof(unsigned char), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

short __VERIFIER_nondet_short()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(short);
	//short val = 0;
	int c;
	short * val_ptr = fuSeBMC_push_in_input_list(_short,NULL,sizeof(short));
	if ((c = fread(val_ptr ,1 , sizeof(short), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

unsigned short __VERIFIER_nondet_ushort()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(unsigned short);
	//unsigned short val = 0;
	int c;
	unsigned short * val_ptr = fuSeBMC_push_in_input_list(_ushort,NULL,sizeof(unsigned short));
	if ((c = fread(val_ptr ,1 , sizeof(unsigned short), stdin)) > 0) 
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

int __VERIFIER_nondet_int()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//fuSeBMC_log_info("We are in __VERIFIER_nondet_int()\n");
	//(*fuSeBMC_input_size_ptr) += sizeof(int);
	//int val = 0;
	int c;
	int * val_ptr = fuSeBMC_push_in_input_list(_int,NULL,sizeof(int));
	//setvbuf(stdin, (char*)NULL, _IOFBF, 0);// full buffering mode
	if ((c = fread(val_ptr ,1 ,sizeof(int), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		//fuSeBMC_log_info("Input=%d\n",* val_ptr);
		return * val_ptr;
	}
	
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}
int __VERIFIER_nondet_int_OK()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	int val = 0;
	int c;
	//setvbuf(stdin, (char*)NULL, _IOFBF, 0);// full buffering mode
	// read Int from STDIN.
	if ((c = fread(&val ,1 ,fuSeBMC_get_sizeof_inputType(_int), stdin)) > 0)
	{
		//Store the Value in the input_list to be exported as Testcase if needed.
		fuSeBMC_push_in_input_list(_int,&val,0);
		//fuSeBMC_Write_OneInput_in_Testcase(_int,&val);
		pthread_mutex_unlock(fuSeBMC_lock);
		//fuSeBMC_log_info("from Fuzz val=%d\n",val);
		return val;
	}
	val = (int)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_log_info("NOT from Fuzz val=%d\n",val);
	fuSeBMC_push_in_input_list(_int,&val,0);
	//fuSeBMC_Write_OneInput_in_Testcase(_int,&val);
	//fuSeBMC_send_signal_to_fuzzer(SIGUSR2);
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

unsigned int __VERIFIER_nondet_uint()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(unsigned int);
	//unsigned int val = 0;
	int c;
	unsigned int * val_ptr = fuSeBMC_push_in_input_list(_uint,NULL,sizeof(unsigned int));
	if ((c = fread(val_ptr ,1 , sizeof(unsigned int), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

long __VERIFIER_nondet_long()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(long);
	//long val = 0;
	int c;
	long * val_ptr = fuSeBMC_push_in_input_list(_long,NULL,sizeof(long));
	if ((c = fread(val_ptr ,1 , sizeof(long), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

unsigned long __VERIFIER_nondet_ulong()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(unsigned long);
	//unsigned long val = 0;
	int c;
	unsigned long * val_ptr = fuSeBMC_push_in_input_list(_ulong,NULL,sizeof(unsigned long));
	if ((c = fread(val_ptr ,1 , sizeof(unsigned long), stdin)) > 0) 
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr ;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr ;
}

long long __VERIFIER_nondet_longlong()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(long long);
	//long long val = 0;
	int c;
	long long * val_ptr = fuSeBMC_push_in_input_list(_longlong,NULL,sizeof(long long));
	if ((c = fread(val_ptr,1 , sizeof(long long), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

unsigned long long __VERIFIER_nondet_ulonglong()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(unsigned long long);
	//unsigned long long val = 0;
	int c;
	unsigned long long * val_ptr = fuSeBMC_push_in_input_list(_ulonglong,NULL,sizeof(unsigned long long));
	if ((c = fread(val_ptr ,1 , sizeof(unsigned long long), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

float __VERIFIER_nondet_float()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(float);
	//float val = 0;
	int c;
	float * val_ptr = fuSeBMC_push_in_input_list(_float,NULL,sizeof(float));
	if ((c = fread(val_ptr ,1 , sizeof(float), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

double __VERIFIER_nondet_double()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(double);
	//double val = 0;
	int c;
	double * val_ptr = fuSeBMC_push_in_input_list(_double,NULL,sizeof(double));
	if ((c = fread(val_ptr ,1 , sizeof(double), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

_Bool __VERIFIER_nondet_bool()
{
	//return (_Bool)__VERIFIER_nondet_int();
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	//(*fuSeBMC_input_size_ptr) += sizeof(_Bool);
	//_Bool val = 0;
	_Bool * val_ptr = fuSeBMC_push_in_input_list(_bool,NULL,sizeof(_Bool));
	int c;
	if ((c = fread(val_ptr ,1 ,sizeof(_Bool), stdin)) > 0)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return * val_ptr;
	}
	* val_ptr = 0 ;
	pthread_mutex_unlock(fuSeBMC_lock);
	return * val_ptr;
}

void *__VERIFIER_nondet_pointer()
{
	return (void *)__VERIFIER_nondet_ulong(); 
}

 unsigned int __VERIFIER_nondet_size_t()
{
	return __VERIFIER_nondet_uint();
}

unsigned char __VERIFIER_nondet_u8()
{
	return __VERIFIER_nondet_uchar();
}

unsigned short __VERIFIER_nondet_u16()
{
	return __VERIFIER_nondet_ushort();
}

unsigned int __VERIFIER_nondet_u32()
{
	return __VERIFIER_nondet_uint();
}

unsigned int __VERIFIER_nondet_U32()
{
	return __VERIFIER_nondet_u32();
}

unsigned char __VERIFIER_nondet_unsigned_char()
{
	return __VERIFIER_nondet_uchar();
}

unsigned int __VERIFIER_nondet_unsigned()
{
	return __VERIFIER_nondet_uint();
}

// SEE: https://stackoverflow.com/q/39431924


const char *__VERIFIER_nondet_string()
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	if(fuSeBMC_IsRandomHasSeed == 0)
	{
		//srand(time(0));
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	
	for(int i = 0; i < 10; i++)rand();
	
	int str_length = (rand() %
		(FUSEBMC_MAX_STRING_SIZE - FUSEBMC_MIN_STRING_SIZE + 1)) + FUSEBMC_MIN_STRING_SIZE;
	
	char * val = malloc(sizeof(char) *  + 1); // +1 for '\0'
	memset(val, '\0' , str_length + 1);
	int c = 0;
	if ((c = fread(val, sizeof(char), str_length , stdin)) >= FUSEBMC_MIN_STRING_SIZE)
	{
		fuSeBMC_push_in_input_list(_string, val,str_length);
		pthread_mutex_unlock(fuSeBMC_lock);
		return val;
	}
	fuSeBMC_push_in_input_list(_string,val,str_length);
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}


void fuseGoalCalled(FUSEBMC_goal_t  goal)
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	last_goal = goal;
	//fuSeBMC_print_val_in_file(fuSeBMC_goal_covered_by_this_testcase_file,"#pid=%d\n",getpid());
	
	//fuSeBMC_print_val_in_file(fuSeBMC_goal_covered_by_this_testcase_file,"%lu\n",goal);
	/*if(inputIndex > 20)
	{
		__assert_fail ("0", "32_1_cilled_ok_nondet_linux-3.4-32_1-drivers--media--dvb--frontends--dvb_dummy_fe.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c", 3, __extension__ __PRETTY_FUNCTION__); 
		kill(getppid(), SIGINT);
	}*/
	//FuSeBMC_goal_node_t * search_node = fuSeBMC_find_in_goal_list(fuSeBMC_goal_list_head,goal);
	//if(search_node == NULL)
	
	//int bytePos = goal / (sizeof(char) * CHAR_BIT);
	//int bitPos = goal %  (sizeof(char) * CHAR_BIT);
	
	//char * tmpPtr = fuSeBMC_bitset_arr + bytePos;
	//OK
	//unsigned char bit = (((unsigned char)fuSeBMC_bitset_arr[bytePos]) >> bitPos) & (unsigned char)1;
	//unsigned char bit = ((unsigned char)fuSeBMC_bitset_arr[bytePos]) & ((unsigned char)(UINT8_C(1)<< bitPos));
	
	//if(fuSeBMC_findGoal(goal) < 0)
	//if((fuSeBMC_IsNewGoalsAdded ==1 && bucket_idx != -1) || bit == UINT8_C(0))
	//if((fuSeBMC_IsNewGoalsAdded ==1 && bucket_idx != -1) || fuSeBMC_bitset_arr[goal] == 0)
	//if((fuSeBMC_IsNewGoalsAdded == 1 &&  bucket_idx > -1) || fuSeBMC_bitset_arr[goal] == 0 )
	if(fuSeBMC_bitset_arr[goal] == 0)
	{
		//fuSeBMC_push_in_goal_list(&fuSeBMC_goal_list_head , goal, '1'); // '1': new goal
		//fuSeBMC_addGoal(goal);
		
		//OK
		//fuSeBMC_bitset_arr[bytePos] |= ((unsigned char)(UINT8_C(1) << bitPos));
		
		// NEW CODE : BEGIN
		//int inputs_count = fuSeBMC_count_input_list(fuSeBMC_input_list_head);
		//fuSeBMC_print_val_in_file ("./count.txt","%d\n", inputs_count);
		//fuSeBMC_log_info("goal="FUSEBMC_goal_format"\n",goal);
		
		/*fuSeBMC_Write_InputList_in_Testcase(fuSeBMC_test_case_file);
		*/
		// cover-branches
		if(fuSeBMC_category == 2)
		{
			fuSeBMC_Write_InputList_in_Testcase_CoverBranches();
			fuSeBMC_clear_input_list();
			fuSeBMC_bitset_arr[goal] = 1;
			fuSeBMC_IsNewGoalsAdded = 1;
			//if(fuSeBMC_input_list_head != NULL)fuSeBMC_log_error("fuSeBMC_input_list_head is not null");
		}
		/*FILE* fPtr = fopen("./FuSeBMC_Fuzzer_goals_covered.txt", "a");
		if(fPtr == NULL)
		{
			printf("Error: cannot open file:FuSeBMC_Fuzzer_goals_covered.txt!");
			fuSeBMC_log_error("Error: cannot open file:FuSeBMC_Fuzzer_goals_covered.txt");
		}
		else
		{
			//if(fuSeBMC_IsFirstElementInTestcase == 1)fprintf(fPtr,"#%s\n",fuSeBMC_test_case_file);
			fprintf(fPtr,"%lu\n",goal);
			fclose(fPtr);
		}*/
		
		
		// NEW CODE : END

	}
	pthread_mutex_unlock(fuSeBMC_lock);
}
void fuSeBMC_setup_signal_handlers()
{
	struct sigaction sa;
	sa.sa_handler = NULL;
	sa.sa_flags = SA_RESTART;
	sa.sa_sigaction = NULL;
	sigemptyset(&sa.sa_mask);
	
	//sa.sa_handler = fuSeBMC_SIGUSR2;
	//sigaction(SIGUSR2, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGSEGV;
	sigaction(SIGSEGV, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGABRT;
	sigaction(SIGABRT, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGINT;
	sigaction(SIGINT, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGALRM;
	sigaction(SIGALRM, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGTERM;
	sigaction(SIGTERM, &sa, NULL);
	
	struct itimerval it;
	// cover-branches
	if(fuSeBMC_category == 2)
		it.it_value.tv_sec = FUSEBMC_COVERBRANCHES_TIMEOUT; // seconds
	else 
		// ErrorCall
		//if(fuSeBMC_category == 1)
			it.it_value.tv_sec = FUSEBMC_ERRORCALL_TIMEOUT;
	//it.it_value.tv_usec = (timeout % 1000) * 1000;
	setitimer(ITIMER_REAL, &it, NULL);
	//fuSeBMC_log_info("void fuSeBMC_setup_signal_handlers();\n");
}

void fuSeBMC_SIGSEGV(int sig)
{
	// If TCGen send us IUSER"; We kill the fuzzer.
	
	// Kill the Parent Fuzzer.
	//kill(getppid(), SIGINT);
	//fuSeBMC_log_info("fuSeBMC_SIGSEGV()\n");
	exit(0);
}
void fuSeBMC_SIGABRT(int sig)
{
	//fuSeBMC_log_info("void fuSeBMC_SIGABRT();\n");
	exit(0);
}
void fuSeBMC_SIGINT(int sig)
{
	exit(0);
}
void fuSeBMC_SIGALRM(int sig)
{
	//fuSeBMC_log_info("void fuSeBMC_SIGALRM();\n");
	exit(0);
}
void fuSeBMC_SIGTERM(int sig)
{
	//fuSeBMC_log_info("void fuSeBMC_SIGTERM();\n");
	exit(0);
}
/*void fuSeBMC_send_signal_to_fuzzer(int sig)
{
	return;
	__pid_t fuzzer_pid = getppid();
	if(fuzzer_pid > 0)
		kill(fuzzer_pid, sig);
}*/
#ifdef __cplusplus
}
#endif
