#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdarg.h>
#include <config.h>
#include <FuSeBMC_SeedGenLib.h>


#ifdef __cplusplus
extern "C" {
#endif

//extern struct _IO_FILE * stdin;
//extern struct _IO_FILE * stderr;
//extern char * fgets (char *__restrict __s, int __n, FILE *__restrict __stream);
//extern void * memcpy (void *__restrict __dest, const void *__restrict __src, size_t __n) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
//extern char * strcat (char *__restrict __dest, const char *__restrict __src) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
//#define FUSEBMC_MAX_INPUT_SIZE 3000
//configurations


static unsigned char fuSeBMC_IsRandomHasSeed = 0;
static const char fuSeBMC_alphanum[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuv";
static const int fuSeBMC_alphanum_len = sizeof(fuSeBMC_alphanum) - 1;
static char * fuSeBMC_seed_fn = NULL;
static int current_seed_size = 0;

static int * fuSeBMC_selective_inputs_arr = NULL;
static int fuSeBMC_selective_inputs_count = 0;
static int fuSeBMC_isSelectiveInputsFromMain = 0;

//static char outFileName[100];

static void fuSeBMC_print_val_in_file (char * file_name , char * format, ...)
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
static void fuSeBMC_log_error (char * format, ...)
{
	//return;
	FILE * fPtr = fopen("./SeedGen_error.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot read file:%s\n" , "./SeedGen_error.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}
static void fuSeBMC_log_input(char * format, ...)
{
	//return;
	FILE * fPtr = fopen("./SeedGen_info.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot read file:%s\n" , "./SeedGen_info.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}
void fuSeBMC_load_selective_inputs()
{
	if(access(FUSEBMC_FUZZER_SELECTIVE_INPUTS_FILE, F_OK ) == 0)
	{
		FILE* fPtr = fopen(FUSEBMC_FUZZER_SELECTIVE_INPUTS_FILE, "r");
		if(fPtr == NULL)
		{
			return;
		}
		int input = 0;
		int count = 0;
		fuSeBMC_selective_inputs_arr = malloc(sizeof(int) * FuSEBMC_SELECTIVE_INPUTS_MAX_COUNT);
		if(!feof(fPtr))
		{
			int res = fscanf(fPtr, "%d", &input);
			if(res == 1)
			{
				if(input == FuSEBMC_IS_SELECTIVE_INPUTS_FROM_MAIN)
					fuSeBMC_isSelectiveInputsFromMain = 1;
				else
					fuSeBMC_isSelectiveInputsFromMain = 0;
			}
		}
		while (!feof(fPtr))
		{
			int res = fscanf(fPtr, "%d", &input);
			if(res == 1)
			{
				fuSeBMC_selective_inputs_arr[count] = input;
				count ++;
				if(count >= FuSEBMC_SELECTIVE_INPUTS_MAX_COUNT)
					break;
			}
		}
		fuSeBMC_selective_inputs_count = count;
		//fuSeBMC_log_input("fuSeBMC_selective_inputs_count=%d\n",fuSeBMC_selective_inputs_count);
		fclose(fPtr);
	}
}
/*void fuSeBMC_add_new_size(int p_size)
{
	_Bool isFirstInput = fuSeBMC_total_input_size == 0;
	fuSeBMC_total_input_size += p_size;
	FILE * fPtr = fopen("./SeedGen_size.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot read file:%s\n" , "./SeedGen_size.txt");
		return;

	}
	if(isFirstInput)
		fprintf (fPtr, "###########\n");
	fprintf (fPtr, "%d\n", fuSeBMC_total_input_size);
	fclose(fPtr);
}*/
void fuSeBMC_init()
{
	fuSeBMC_load_selective_inputs();
}
static void fuSeBMC_generate_random_input(void * input_ptr,int length)
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	//char * rnd_input = malloc(sizeof(char) * length ); 
	char * tmp_ptr = input_ptr;
	//memset(rnd_text, '\0',length);
	for(int i = 0; i < length; ++i)
	{
		*tmp_ptr = fuSeBMC_alphanum[rand() % fuSeBMC_alphanum_len];
		tmp_ptr++;
	}
	//*tmp_ptr = '\0';
	//return rnd_input;
}
static char fuSeBMC_generate_random_number_signed()
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	int max_range = FUSEBMC_MAX_RANDOM;
	int min_range = FUSEBMC_MIN_RANDOM;
	char rnd_input = (rand() % (max_range - min_range + 1)) + min_range;
	if(FUSEBMC_GENERATE_POSITIV_AND_NEGATIV)
		if(rand() % 2 == 0) rnd_input *= -1;
	if(FUSEBMC_GENERATE_INPUT_INFO)
		fuSeBMC_log_input("%d\n", (int)rnd_input);
	return rnd_input;
}
static char fuSeBMC_generate_random_number_unsigned()
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	int max_range = FUSEBMC_MAX_RANDOM;
	int min_range = FUSEBMC_MIN_RANDOM;
	char rnd_input = (rand() % (max_range - min_range + 1)) + min_range;
	//if(rand() % 2 == 0) return rnd_input;
	if(FUSEBMC_GENERATE_INPUT_INFO)
		fuSeBMC_log_input("%d\n", (int)rnd_input);
	return rnd_input;
}
static unsigned int fuSeBMC_generate_random_number_unsigned_between(int min, int max)
{
	if(!fuSeBMC_IsRandomHasSeed)
	{
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	unsigned int rnd_input = (rand() % (max - min + 1)) + min;
	//if(rand() % 2 == 0) return rnd_input;
	return rnd_input;
}
static void fuSeBMC_export_input_to_seed(const void * p_ptr, size_t p_size)
{
	if(fuSeBMC_seed_fn == NULL)
	{

		char * fn = malloc(sizeof(char) * SEED_FILE_NAME_RANDOM_PART_LENGTH + 1);
		int fn_len = 16 + SEED_FILE_NAME_RANDOM_PART_LENGTH +1; //+1: for '\0';
		fuSeBMC_seed_fn = malloc(sizeof(char) * fn_len); 
		while(1)
		{
			memset(fn,'\0',SEED_FILE_NAME_RANDOM_PART_LENGTH + 1);
			fuSeBMC_generate_random_input(fn, SEED_FILE_NAME_RANDOM_PART_LENGTH);
			snprintf(fuSeBMC_seed_fn,fn_len, "./seeds/SED_%s.bin",fn);
			fuSeBMC_seed_fn[fn_len] = '\0';
			if(access(fuSeBMC_seed_fn, F_OK ) == 0 )
			{
				// file exists
				//free(tmp_random_str);
			}
			else break;
		}
		free(fn);
	}
	
	FILE *fp = fopen(fuSeBMC_seed_fn,"a+b"); //a: append, b: binary
	if(fp == NULL)
	{
		printf("cannot open file: %s \n",fuSeBMC_seed_fn);
		fuSeBMC_log_error("cannot open file: %s \n",fuSeBMC_seed_fn);
		exit(-1);
	}
	fwrite(p_ptr,p_size,1,fp);
	fclose(fp);
	current_seed_size += p_size;
	if(current_seed_size >= FUSEBMC_MAX_SEED_SIZE)
		exit(0);
}
void fuSeBMC_reach_error()
{
	printf("fuSeBMC_reach_error is reached !!");
	//fuSeBMC_Write_InputList_in_Testcase_ErrorCall();
	fuSeBMC_print_val_in_file("./fuSeBMC_reach_error.txt","%s\n","fuSeBMC_reach_error");
	//if(access(FUSEBMC_TESTCASE_FILENAME_ERROR_CALL, F_OK) == 0 )
	{
		// file exists
		/*char zip_command[1024];
		memset(zip_command,'\0',1024);
		snprintf(zip_command, 1024, "zip -j ./test-suite.zip %s", FUSEBMC_TESTCASE_FILENAME_ERROR_CALL); // -j Junk path; don't add path.
		system(zip_command);*/
	}
	// Kill the Parent Fuzzer.
	//kill(getppid(), SIGINT);		
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

char __VERIFIER_nondet_char()
{
	char val;
	//fuSeBMC_generate_random_input(&val,sizeof(char));
	val =(char)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(char));
	fuSeBMC_export_input_to_seed(&val,sizeof(char));
	return val;
}

unsigned char __VERIFIER_nondet_uchar()
{
	unsigned char val;
	//fuSeBMC_generate_random_input(&val,sizeof(unsigned char));
	val =(unsigned char)fuSeBMC_generate_random_number_unsigned();
	//fuSeBMC_add_new_size(sizeof(unsigned char));
	fuSeBMC_export_input_to_seed(&val,sizeof(unsigned char));
	return val;
}

short __VERIFIER_nondet_short()
{
	short val;
	//fuSeBMC_generate_random_input(&val,sizeof(short));
	val =(short)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(short));
	fuSeBMC_export_input_to_seed(&val,sizeof(short));
	return val;
}

unsigned short __VERIFIER_nondet_ushort()
{
	unsigned short val;
	//fuSeBMC_generate_random_input(&val,sizeof(unsigned short));
	val =(unsigned short)fuSeBMC_generate_random_number_unsigned();
	//fuSeBMC_add_new_size(sizeof(unsigned short));
	fuSeBMC_export_input_to_seed(&val,sizeof(unsigned short));
	return val;
}

int __VERIFIER_nondet_int()
{
	int val;
	//fuSeBMC_generate_random_input(&val,sizeof(int));
	if(fuSeBMC_selective_inputs_count > 0)
	{
		if(current_seed_size == 0 && fuSeBMC_isSelectiveInputsFromMain == 0)
			val = 0;
		else
			val = (int)fuSeBMC_selective_inputs_arr[fuSeBMC_generate_random_number_unsigned_between(0,fuSeBMC_selective_inputs_count-1)];
	}
	else
		val =(int)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(int));
	//fuSeBMC_log_input("val=%d\n",val);
	fuSeBMC_export_input_to_seed(&val,sizeof(int));
	return val;
}

unsigned int __VERIFIER_nondet_uint()
{
	unsigned int val;
	//fuSeBMC_generate_random_input(&val,sizeof(unsigned int));
	val =(unsigned int)fuSeBMC_generate_random_number_unsigned();
	//fuSeBMC_add_new_size(sizeof(unsigned int));
	fuSeBMC_export_input_to_seed(&val,sizeof(unsigned int));
	return val;
}

long __VERIFIER_nondet_long()
{
	long val;
	//fuSeBMC_generate_random_input(&val,sizeof(long));
	val =(long)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(long));
	fuSeBMC_export_input_to_seed(&val,sizeof(long));
	return val;
}

unsigned long __VERIFIER_nondet_ulong()
{
	unsigned long val;
	//fuSeBMC_generate_random_input(&val,sizeof(unsigned long));
	val =(unsigned long)fuSeBMC_generate_random_number_unsigned();
	//fuSeBMC_add_new_size(sizeof(unsigned long));
	fuSeBMC_export_input_to_seed(&val,sizeof(unsigned long));
	return val;
}

long long __VERIFIER_nondet_longlong()
{
	long long val;
	//fuSeBMC_generate_random_input(&val,sizeof(long long));
	val =(long long)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(long long));
	fuSeBMC_export_input_to_seed(&val,sizeof(long long));
	return val;
}

unsigned long long __VERIFIER_nondet_ulonglong()
{
	unsigned long long val;
	//fuSeBMC_generate_random_input(&val,sizeof(unsigned long long));
	val =(unsigned long long)fuSeBMC_generate_random_number_unsigned();
	//fuSeBMC_add_new_size(sizeof(unsigned long long));
	fuSeBMC_export_input_to_seed(&val,sizeof(unsigned long long));
	return val;
}

float __VERIFIER_nondet_float()
{
	float val;
	//fuSeBMC_generate_random_input(&val,sizeof(float));
	val =(float)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(float));
	fuSeBMC_export_input_to_seed(&val,sizeof(float));
	return val;
}

double __VERIFIER_nondet_double()
{
	double val;
	//fuSeBMC_generate_random_input(&val,sizeof(double));
	val =(double)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(double));
	fuSeBMC_export_input_to_seed(&val,sizeof(double));
	return val;
}

_Bool __VERIFIER_nondet_bool()
{
	_Bool val;// =  (_Bool)__VERIFIER_nondet_int();
	//fuSeBMC_add_new_size(sizeof(_Bool));
	//fuSeBMC_log_input("_Bool=%d\n",val);
	//fuSeBMC_log_input("%d\n",val);

	val =(_Bool)fuSeBMC_generate_random_number_signed();
	//fuSeBMC_add_new_size(sizeof(_Bool));
	fuSeBMC_export_input_to_seed(&val,sizeof(_Bool));
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


const char *__VERIFIER_nondet_string()
{
	int str_length = (rand() % 
		(FUSEBMC_MAX_STRING_SIZE - FUSEBMC_MIN_STRING_SIZE + 1)) + FUSEBMC_MIN_STRING_SIZE;
	char *val = malloc(str_length+1);
	fuSeBMC_generate_random_input(val,str_length);
	//fuSeBMC_add_new_size(str_length);
	memset(val, '\0' , str_length+1);
	fuSeBMC_export_input_to_seed(val,str_length+1);
	return val;
}

#ifdef __cplusplus
}
#endif