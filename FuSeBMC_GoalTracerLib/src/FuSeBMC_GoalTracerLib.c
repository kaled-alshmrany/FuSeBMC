#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdarg.h>

#include <limits.h>
#include <config.h>
#include <FuSeBMC_GoalTracerLib.h>
#include <goalList.h>

#ifdef TRACER_EXPORT_TESTCASE
#include <inputList.h>
unsigned char fuSeBMC_IsRandomHasSeed = 0;
int fuSeBMC_NumOfInputsInTestcase = 0;
#endif
#ifdef __cplusplus
extern "C" {
#endif

extern struct _IO_FILE * stdin;
extern struct _IO_FILE * stderr;
extern char * fgets (char *__restrict __s, int __n, FILE *__restrict __stream);
extern void * memcpy (void *__restrict __dest, const void *__restrict __src, size_t __n) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
extern char * strcat (char *__restrict __dest, const char *__restrict __src) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
char * fuSeBMC_get_input();

// This file is part of TestCov,
// a robust test executor with reliable coverage measurement:
// https://gitlab.com/sosy-lab/software/test-suite-validator/
//
// Copyright (C) 2018 - 2020  Dirk Beyer
// SPDX-FileCopyrightText: 2019 Dirk Beyer <https://www.sosy-lab.org>
//
// SPDX-License-Identifier: Apache-2.0

#define FUSEBMC_MAX_INPUT_SIZE 3000
pthread_mutex_t * fuSeBMC_lock = NULL;
int fuSeBMC_no_more_input = 0;
//int fuSeBMC_input_is_invalid = 0;

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
	FILE * fPtr = fopen("./Tracer_error.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot read file:%s\n" , "./Tracer_error.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	fprintf (fPtr, "\n++++++++++++++++++++++++++\npid=%d\n",getpid());
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}
void fuSeBMC_log_info(char * format, ...)
{
	//return;
	FILE * fPtr = fopen("./Tracer_info.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot read file:%s\n" , "./Tracer_info.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	fprintf (fPtr, "\n++++++++++++++++++++++++++\npid=%d\n",getpid());
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
	
}
void fuSeBMC_abort_prog()
{
	exit(0);
}

void __VERIFIER_assume(int cond)
{
	if (!cond)
	{
		fuSeBMC_abort_prog();
	}
}

void __VERIFIER_error()
{
	// You can Implement it to check if '__VERIFIER_error()' is called.
	exit(0);

}

#ifdef TRACER_EXPORT_TESTCASE
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
#endif
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
#ifdef TRACER_EXPORT_TESTCASE
void fuSeBMC_Write_OneInput_in_Testcase(char * format, ...)
{
	if(fuSeBMC_NumOfInputsInTestcase > TRACER_MAX_NUM_IN_TESTCASE)
	{
		fuSeBMC_log_error("fuSeBMC_NumOfInputsInTestcase=%d\n",fuSeBMC_NumOfInputsInTestcase);
		exit(9);
	}
	FILE *fptr = fopen(TRACER_TESTCASE_FILENAME, "a");
	if(fptr == NULL)
	{
		printf("Error: cannot write file:%s\n", TRACER_TESTCASE_FILENAME);
		fuSeBMC_log_error("Error: cannot write file:%s\n", TRACER_TESTCASE_FILENAME);
		exit(0);
	}
	fuSeBMC_NumOfInputsInTestcase ++;
	//fseek(fptr, -11, SEEK_END);
	va_list args;
	va_start (args, format);
	vfprintf (fptr, format, args);
	va_end (args);
	//fprintf(fptr,"</testcase>");
	fclose(fptr);
}

#endif

// taken from https://stackoverflow.com/a/32496721
void fuSeBMC_replace_char(char *str, char find, char replace)
{
	char *current_pos = strchr(str, find);
	while (current_pos)
	{
		*current_pos = replace;
		current_pos = strchr(current_pos, find);
	}
}

void fuSeBMC_parse_input_from(char *inp_var, char *format, void *destination)
{
	char format_with_fallback[13];
	strcpy(format_with_fallback, format);
	strcat(format_with_fallback, "%c%c%c%c");
	if (inp_var[0] == '0' && inp_var[1] == 'x')
	{
		fuSeBMC_replace_char(format_with_fallback, 'd', 'x');
		fuSeBMC_replace_char(format_with_fallback, 'u', 'x');
	}
	else
	{
		if (inp_var[0] == '\'' || inp_var[0] == '\"')
		{
			int inp_length = strlen(inp_var);
			// Remove ' at the end
			inp_var[inp_length - 1] = '\0';
			// Remove ' in the beginning
			inp_var++;
		}
	}
	char leftover[4];
	int filled = sscanf(inp_var, format_with_fallback, destination, &leftover[0],
			&leftover[1], &leftover[2], &leftover[3]);
	_Bool is_valid = 1;
	if (filled == 5 || filled == 0)
	{
		is_valid = 0;
	}
	while (filled > 1) 
	{
		filled--;
		char literal = leftover[filled - 1];
		switch (literal)
		{
			case 'l':
			case 'L':
			case 'u':
			case 'U':
			case 'f':
			case 'F':
				break;
			default:
				is_valid = 0;
		}
	}
	if (!is_valid)
	{
		fprintf(stderr, "Can't parse input: '%s'\n", inp_var);
		fuSeBMC_log_error("Can't parse input: '%s' with format '%s'; fuSeBMC_NumOfInputsInTestcase=%d.\n",
				inp_var, format,fuSeBMC_NumOfInputsInTestcase);
		fuSeBMC_abort_prog();
	}
}

void fuSeBMC_parse_input(char *format, void *destination)
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	char * inp_var = fuSeBMC_get_input();
	if(fuSeBMC_no_more_input == 1)
	{
		
	}
	else
		fuSeBMC_parse_input_from(inp_var, format, destination);
	
	// NEW
	free(inp_var);
}

char __VERIFIER_nondet_char()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	char val;
	char * inp_var = fuSeBMC_get_input();
	if(fuSeBMC_no_more_input == 1)
	{
		
	}
	else
	if (inp_var[0] == '\'')
	{
		fuSeBMC_parse_input_from(inp_var, "%c", &val);
	} 
	else 
	{
		fuSeBMC_parse_input_from(inp_var, "%hhd", &val);
	}
	free(inp_var);
	//fuSeBMC_log_input("char=%d\n",val);
	//fuSeBMC_log_input("%d\n",val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"char\">%hhd</input>\n",val);
	}

#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

unsigned char __VERIFIER_nondet_uchar()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	unsigned char val;
	fuSeBMC_parse_input("%hhu", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"unsigned char\">%hhu</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

short __VERIFIER_nondet_short()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	short val;
	fuSeBMC_parse_input("%hd", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"short\">%hd</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

unsigned short __VERIFIER_nondet_ushort()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	unsigned short val;
	fuSeBMC_parse_input("%hu", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"unsigned short\">%hu</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

int __VERIFIER_nondet_int()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	int val;
	fuSeBMC_parse_input("%d", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"int\">%d</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

unsigned int __VERIFIER_nondet_uint()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	unsigned int val;
	fuSeBMC_parse_input("%u", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"unsigned int\">%u</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

long __VERIFIER_nondet_long()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	long val;
	fuSeBMC_parse_input("%ld", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"long\">%ld</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

unsigned long __VERIFIER_nondet_ulong()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	unsigned long val;
	fuSeBMC_parse_input("%lu", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"unsigned long\">%lu</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

long long __VERIFIER_nondet_longlong()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	long long val;
	fuSeBMC_parse_input("%lld", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"long long\">%lld</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

unsigned long long __VERIFIER_nondet_ulonglong()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	unsigned long long val;
	fuSeBMC_parse_input("%llu", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"unsigned long long\">%llu</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

float __VERIFIER_nondet_float()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	float val;
	fuSeBMC_parse_input("%f", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"float\">%.18e</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

double __VERIFIER_nondet_double()
{
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	double val;
	fuSeBMC_parse_input("%lf", &val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"double\">%.18e</input>\n",val);
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

_Bool __VERIFIER_nondet_bool()
{
	_Bool val = (_Bool)__VERIFIER_nondet_int();
	
	//fuSeBMC_log_input("_Bool=%d\n",val);
	//fuSeBMC_log_input("%d\n",val);
	return val;
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
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	pthread_mutex_lock(fuSeBMC_lock);
	char *val = malloc(FUSEBMC_MAX_INPUT_SIZE + 1);
	// Read to end of line
	fuSeBMC_parse_input("%[^\n]", val);
#ifdef TRACER_EXPORT_TESTCASE
	if(fuSeBMC_no_more_input == 1)
	{
		val = 0;
		fuSeBMC_Write_OneInput_in_Testcase("<input type=\"string\">%s</input>\n",fuSeBMC_string2hexString(val));
	}
#endif
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

char * fuSeBMC_get_input()
{
	char * inp_var = malloc(FUSEBMC_MAX_INPUT_SIZE);
	char * result = fgets(inp_var, FUSEBMC_MAX_INPUT_SIZE, stdin);
	if (result == 0)
	{
#ifdef TRACER_EXPORT_TESTCASE
		fuSeBMC_no_more_input = 1;
		return inp_var;
#else
		fprintf(stderr, "No more test inputs available, exiting\n");
		exit(4);
#endif
	}
	unsigned int input_length = strlen(inp_var)-1;
	/* Remove '\n' at end of input */
	if (inp_var[input_length] == '\n')
	{
		inp_var[input_length] = '\0';
	}
	return inp_var;
}


void fuSeBMC_return(int code){exit(code);}
//void fuSeBMC_init()
//{
	//fuSeBMC_log_info("fuSeBMC_init is called\n");
	/*if(fuSeBMC_lock == NULL)
	{
		fuSeBMC_lock = malloc(sizeof(pthread_mutex_t));
		if (pthread_mutex_init(fuSeBMC_lock, NULL) != 0)
		{
			printf("\n mutex init failed\n");
			fuSeBMC_log_error("mutex init failed\n");
			exit(5);
		}
		fuSeBMC_create_goal_list();
	}*/
//}
void fuSeBMC_init()
{
	fuSeBMC_init_mutex();
}
void fuSeBMC_init_mutex()
{
	if(fuSeBMC_lock == NULL)
	{
		fuSeBMC_lock = malloc(sizeof(pthread_mutex_t));
		if (pthread_mutex_init(fuSeBMC_lock, NULL) != 0)
		{
			printf("\n mutex init failed\n");
			fuSeBMC_log_error("mutex init failed\n");
			exit(5);
		}
		else
		{
			//fuSeBMC_log_info("fuSeBMC_init_mutex Done\n");
		}
		pthread_mutex_lock(fuSeBMC_lock);
		fuSeBMC_create_goal_list();
#ifdef TRACER_EXPORT_TESTCASE
		//if(buckets_arr == NULL) fuSeBMC_create_input_list();
#endif
		pthread_mutex_unlock(fuSeBMC_lock);
	}
}
void fuseGoalCalled(FUSEBMC_goal_t goal)
{
	//fuSeBMC_log_info("fuseGoalCalled is called\n");
	if(fuSeBMC_lock == NULL)fuSeBMC_init();
	/*if(fuSeBMC_lock == NULL)
	{
		fuSeBMC_lock = malloc(sizeof(pthread_mutex_t));
		if (pthread_mutex_init(fuSeBMC_lock, NULL) != 0)
		{
			printf("\n mutex init failed\n");
			fuSeBMC_log_error("mutex init failed\n");
			exit(5);
		}
		fuSeBMC_create_goal_list();
	}*/
	pthread_mutex_lock(fuSeBMC_lock);
	if(fuSeBMC_bitset_arr[goal] == 0)
	{
		fuSeBMC_bitset_arr[goal] = 1;
		FILE * fptr;
		fptr = fopen("./goals_covered.txt","a");
		if(fptr == NULL)
		{
			printf("Error: cannot write to file:goals_covered.txt!");
			fuSeBMC_log_error("Error: cannot write to file:goals_covered.txt!");
			pthread_mutex_unlock(fuSeBMC_lock);
			exit(3);
		}
		//fprintf(fptr,"#processid=%d\n",getpid());
		fprintf(fptr,FUSEBMC_goal_format "\n",goal);
		fclose(fptr);
	}
	pthread_mutex_unlock(fuSeBMC_lock);
}
#ifdef __cplusplus
}
#endif