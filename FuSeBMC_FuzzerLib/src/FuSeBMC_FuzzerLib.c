#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <pthread.h>
//#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <sys/shm.h>
#include <sys/resource.h>
//#include <errno.h>
#include <limits.h>
#include <wait.h>
#include <sys/stat.h>

#include <stdbool.h>
#include <config.h>
#include <FuSeBMC_FuzzerLib.h>


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

//rlim_t mem_limit = 5 * 1024; // 8 GIGA

#define alloc_printf(_str...)({\
	char * _tmp;\
	int32_t _len = snprintf(NULL, 0, _str);\
	if (_len < 0) {fuSeBMC_log_error("Whoa, snprintf() fails?!");exit(0);}\
	_tmp = (char *)malloc(_len + 1);\
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

#define __VERIFIER_NON_DET(Type)\
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();\
	pthread_mutex_lock(fuSeBMC_lock);\
	(*fuSeBMC_input_size_ptr) += sizeof(Type);\
	if((fuSeBMC_stdin_consumed + sizeof(Type)) > fuSeBMC_stdin_len)\
	{\
		pthread_mutex_unlock(fuSeBMC_lock);\
		return 0;\
	}\
	fuSeBMC_stdin_consumed += sizeof(Type);\
	Type * val_ptr =(Type *)fuSeBMC_stdin_curr;\
	fuSeBMC_stdin_curr += sizeof(Type);\
	pthread_mutex_unlock(fuSeBMC_lock);\
	return * val_ptr;


pthread_mutex_t * fuSeBMC_lock = NULL;
unsigned char fuSeBMC_IsNewGoalsAdded = 0;
unsigned char fuSeBMC_IsRandomHasSeed = 0;
int fuSeBMC_shm_id = -1;
int fuSeBMC_shm_input_size_id = -1;
unsigned char fuSeBMC_IsStdInCopied = 0;
void * fuSeBMC_stdin = NULL;
void * fuSeBMC_stdin_curr = NULL;
unsigned int fuSeBMC_stdin_len = 0 , fuSeBMC_stdin_consumed = 0;
unsigned int * fuSeBMC_input_size_ptr = NULL;
char * fuSeBMC_bitset_arr = NULL;
int fuSeBMC_env_goals_cnt = 0;
//FUSEBMC_goal_t fuSeBMC_bitset_sz_byte = 0;



FUSEBMC_goal_t last_goal= 0;

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
	fprintf (fPtr, "\n++++++++++++++++++++++++++\npid=%d\n",getpid());
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
}

void fuSeBMC_log_error (char * format, ...)
{
	//return;
	FILE * fPtr = fopen("./Fuzzer_error.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot write file:%s\n" , "./Fuzzer_error.txt");
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
	FILE * fPtr = fopen("./Fuzzer_info.txt", "a");
	if(fPtr == NULL)
	{
		printf("Error: cannot write file:%s\n" , "./Fuzzer_info.txt");
		return;
	}
	va_list args;
	va_start (args, format);
	fprintf (fPtr, "\n++++++++++++++++++++++++++\npid=%d\n",getpid());
	vfprintf (fPtr, format, args);
	va_end (args);
	fclose(fPtr);
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
	if(fuSeBMC_input_size_ptr == NULL)
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
	}
}
#endif //STAND_ALONE
void fuSeBMC_init()
{
	//return;
	//fuSeBMC_init_mutex();
	if(fuSeBMC_IsStdInCopied == 0) fuSeBMC_copy_stdin();
	fuSeBMC_setup_signal_handlers();
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
			pthread_mutex_lock(fuSeBMC_lock);
			fuSeBMC_setup_shm();
			if(fuSeBMC_IsStdInCopied == 0) fuSeBMC_copy_stdin();
			pthread_mutex_unlock(fuSeBMC_lock);
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


void fuSeBMC_reach_error()
{
	//Reach-Error
	if(fuSeBMC_category == 1)
	{
		fuSeBMC_print_val_in_file("./fuSeBMC_reach_error.txt","%s\n","fuSeBMC_reach_error");
		//fuSeBMC_Write_InputList_in_Testcase_ErrorCall();
		//if(access(FUSEBMC_TESTCASE_FILENAME_ERROR_CALL, F_OK) == 0 )
		{
			// file exists
			/*char zip_command[1024];
			memset(zip_command,'\0',1024);
			snprintf(zip_command, 1024, "zip -j ./test-suite.zip %s", FUSEBMC_TESTCASE_FILENAME_ERROR_CALL); // -j Junk path; don't add path.
			system(zip_command);*/
		}
		//if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
		if(fuSeBMC_lock != NULL){ pthread_mutex_lock(fuSeBMC_lock);}
		
		fuSeBMC_run_TC_gen();
		if(fuSeBMC_lock != NULL) {pthread_mutex_unlock(fuSeBMC_lock);}
	}
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
ssize_t fuSeBMC_write(int __fd, const void *__buf, size_t __n)
{
	return write(__fd,__buf,__n);
	//return 0;
}
ssize_t fuSeBMC_read(int __fd, void *__buf, size_t __nbytes)
{
	return read(__fd, __buf, __nbytes);
	//return 0;
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
	//__VERIFIER_NON_DET(char);
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	(*fuSeBMC_input_size_ptr) += sizeof(char);
	if((fuSeBMC_stdin_consumed + sizeof(char)) > fuSeBMC_stdin_len)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return 0;
	}
	fuSeBMC_stdin_consumed += sizeof(char);
	char * val_ptr =(char *)fuSeBMC_stdin_curr;
	fuSeBMC_stdin_curr += sizeof(char);
	pthread_mutex_unlock(fuSeBMC_lock);
	//fuSeBMC_log_info("char=%hhd\n",* val_ptr);
	return * val_ptr;
}

unsigned char __VERIFIER_nondet_uchar()
{
	__VERIFIER_NON_DET(unsigned char);
}

short __VERIFIER_nondet_short()
{
	__VERIFIER_NON_DET(short);
}

unsigned short __VERIFIER_nondet_ushort()
{
	__VERIFIER_NON_DET(unsigned short);
}
int __VERIFIER_nondet_int()
{
	__VERIFIER_NON_DET(int);
}

unsigned int __VERIFIER_nondet_uint()
{
	__VERIFIER_NON_DET(unsigned int);
}
long __VERIFIER_nondet_long()
{
	__VERIFIER_NON_DET(long);
}
unsigned long __VERIFIER_nondet_ulong()
{
	__VERIFIER_NON_DET(unsigned long);
}

long long __VERIFIER_nondet_longlong()
{
	__VERIFIER_NON_DET(long long);
}

unsigned long long __VERIFIER_nondet_ulonglong()
{
	__VERIFIER_NON_DET(unsigned long long);
}

float __VERIFIER_nondet_float()
{
	__VERIFIER_NON_DET(float);
}

double __VERIFIER_nondet_double()
{
	__VERIFIER_NON_DET(double);
}

_Bool __VERIFIER_nondet_bool()
{
	__VERIFIER_NON_DET(_Bool);
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
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	
	/*char *val = malloc(FUSEBMC_MAX_INPUT_SIZE + 1);
	// Read to end of line
	fuSeBMC_parse_input("%[^\n]", val);
	*/
	if(fuSeBMC_IsRandomHasSeed == 0)
	{
		//srand(time(0));
		srand(getpid());
		fuSeBMC_IsRandomHasSeed = 1;
	}
	
	for(int i = 0; i < 10; i++)rand();
	
	//int str_length = rand() % FUSEBMC_MAX_STRING_SIZE;
	int str_length = (rand() %
		(FUSEBMC_MAX_STRING_SIZE - FUSEBMC_MIN_STRING_SIZE + 1)) + FUSEBMC_MIN_STRING_SIZE;
	
	char * val = malloc(sizeof(char) *  + 1); // +1 for '\0'
	memset(val, '\0' , str_length + 1);
	
	(*fuSeBMC_input_size_ptr) += str_length;
	if((fuSeBMC_stdin_consumed + str_length + 1) > fuSeBMC_stdin_len)
	{
		pthread_mutex_unlock(fuSeBMC_lock);
		return val;
	}
	fuSeBMC_stdin_consumed += str_length + 1;
	memcpy(val,fuSeBMC_stdin_curr,str_length);
	fuSeBMC_stdin_curr += str_length;
	pthread_mutex_unlock(fuSeBMC_lock);
	return val;
}

void fuSeBMC_copy_stdin()
{
	///struct stat sb;
	//fstat(stdin->_fileno, &sb);
	if(fuSeBMC_IsStdInCopied == 0)
	{
		fseek(stdin, 0, SEEK_END);
		fuSeBMC_stdin_len = ftell(stdin);
		//fuSeBMC_stdin_len = sb.st_size;
		fuSeBMC_stdin = malloc(fuSeBMC_stdin_len);
		memset(fuSeBMC_stdin,0,fuSeBMC_stdin_len);
		fseek(stdin, 0, SEEK_SET);
		//rewind(stdin);
		fread(fuSeBMC_stdin ,sizeof(char), fuSeBMC_stdin_len , stdin);
		fuSeBMC_stdin_curr = fuSeBMC_stdin;
		//fclose(stdin);
		//fuSeBMC_log_info("fuSeBMC_stdin_len=%u, c = %d\n",fuSeBMC_stdin_len, c);
		fuSeBMC_IsStdInCopied = 1;
	}
}

void fuseGoalCalled(FUSEBMC_goal_t  goal)
{
	if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	pthread_mutex_lock(fuSeBMC_lock);
	last_goal = goal;
	
	if(fuSeBMC_bitset_arr[goal] == 0)
	//if(bit == UINT8_C(0))
	{
		// cover-branches
		if(fuSeBMC_category == 2)
		{
			fuSeBMC_run_TC_gen();
			exit(0);
		}
	}
	pthread_mutex_unlock(fuSeBMC_lock);
}
static pid_t child_pid = (pid_t)0;

void fuSeBMC_run_TC_gen()
{
	//return ;
	//if(fuSeBMC_lock == NULL) fuSeBMC_init_mutex();
	//mypipe[0] is set up for reading, mypipe[1] is set up for writing
	
	int mypipe[2];
	/* Create the pipe. */
	int pipe_res = pipe (mypipe);
	if (pipe_res != 0)
	{
		fuSeBMC_log_error("Pipe failed error=%d.\n",pipe_res);
		exit(0);
	}
	
	//ErrorCall
	if(fuSeBMC_category == 1)
	{
		char * fuzzer_id_ptr = alloc_printf("%s_fuzid",fuSeBMC_run_id);
		char * fuzzer_id_val = alloc_printf("%d",getppid());
		setenv(fuzzer_id_ptr,fuzzer_id_val,1);
	}
	struct rlimit rlimit_afl;
#ifdef RLIMIT_AS
		int getrlimit_res = getrlimit(RLIMIT_AS, &rlimit_afl);
#else
		int getrlimit_res = getrlimit(RLIMIT_DATA, &rlimit_afl);
#endif
	if(getrlimit_res != 0)
		fuSeBMC_log_error("getrlimit failed()\n");
	
	child_pid = fork();
	if (child_pid < 0)
	{
		fuSeBMC_log_error("fork() failed\n");
		exit(0);
	}
	if (child_pid == (pid_t) 0)
	{
		//child
		/* This is the child process. Close other end first. */
		struct rlimit r;
		if (getrlimit_res == 0)
		{
			//r.rlim_max = r.rlim_cur = (rlim_t)(mem_limit << 20);// 1024 * 1024
			r.rlim_max = rlimit_afl.rlim_max;
			r.rlim_cur = rlimit_afl.rlim_cur;
#ifdef RLIMIT_AS
			setrlimit(RLIMIT_AS, &r);
#else
			setrlimit(RLIMIT_DATA, &r);
#endif
		}
		r.rlim_max = r.rlim_cur = 0; // core dump
		setrlimit(RLIMIT_CORE, &r);
		//system("sulimit -c 0");
		//setsid(getsid(getppid()));
		//setsid();
		close(mypipe[1]);
		if (dup2(mypipe[0], STDIN_FILENO) < 0)
		{
			fuSeBMC_log_error("dup2() failed\n");
			exit(0);
		}
		close(mypipe[0]);
		//read_from_pipe (mypipe[0]);
		char * argv[]={"./tcgen.exe", NULL};
		execv("./tcgen.exe", argv);
		
		//char * argv[]={"timeout","10","./tcgen.exe", NULL};
		//execv("timeout 10 ./tcgen.exe", argv);
		
		fuSeBMC_log_error("execv failed.\n");
		
	}
	else
	{
		/* This is the parent process. Close other end first. */
		close(mypipe[0]);
		//write_to_pipe (mypipe[1]);
		//FILE * stream = fdopen (mypipe[1], "w");
		//fprintf (stream, "hello, world!\n");
		//fprintf (stream, "goodbye, world!\n");
		//fclose (stream);
		//fuSeBMC_print_val_in_file("./fuSeBMC_reach_error.txt","fuSeBMC_stdin_len=%u\n",fuSeBMC_stdin_len);
		write(mypipe[1], fuSeBMC_stdin, fuSeBMC_stdin_len);
		close(mypipe[1]);
		int status;
		wait(&status);
		
		//waitpid(child_pid, &status, 0);
		/*pid_t pid_wait;
		while((pid_wait = waitpid(child_pid, &status, WNOHANG)) != child_pid)
		{
			sleep(1);
		}*/
		
	}
}
void fuSeBMC_setup_signal_handlers()
{
	//fuSeBMC_log_info("void fuSeBMC_setup_signal_handlers();\n");
	//signal(SIGINT, SIG_DFL);
	//signal(SIGUSR2, SIG_DFL);
	//signal(SIGABRT, SIG_DFL);
	//signal(SIGTERM, SIG_DFL);
	
	struct sigaction sa;
	sa.sa_handler = NULL;
	sa.sa_flags = SA_RESTART;
	sa.sa_sigaction = NULL;
	sigemptyset(&sa.sa_mask);
	
	sa.sa_handler = fuSeBMC_SIGUSR2;
	sigaction(SIGUSR2, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGSEGV;
	sigaction(SIGSEGV, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGABRT;
	sigaction(SIGABRT, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGINT;
	sigaction(SIGINT, &sa, NULL);
	
	sa.sa_handler = fuSeBMC_SIGTERM;
	sigaction(SIGTERM, &sa, NULL);
}
void fuSeBMC_SIGUSR2(int sig)
{
	// If TCGen send us IUSER"; We kill the fuzzer.
	
	// Kill the Parent Fuzzer.
	//kill(getppid(), SIGINT);
	//if(child_pid > 0)
	//	kill(child_pid, SIGKILL);
	kill(getppid(), SIGTERM);
	exit(0);
}
void fuSeBMC_SIGSEGV(int sig)
{
	// If TCGen send us IUSER"; We kill the fuzzer.
	
	// Kill the Parent Fuzzer.
	//kill(getppid(), SIGINT);
	//fuSeBMC_log_info("fuSeBMC_SIGSEGV()\n");
	//if(child_pid > 0)
	//	kill(child_pid, SIGKILL);
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
void fuSeBMC_SIGTERM(int sig)
{
	//fuSeBMC_log_info("void fuSeBMC_SIGTERM();\n");
	if(child_pid > 0)
		kill(child_pid, SIGKILL);
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
