#ifndef FUSEBMC_FUZZER_LIB_H
#define FUSEBMC_FUZZER_LIB_H
#include <stdint.h>
#include <config.h>

#ifdef __cplusplus
extern "C" {
#endif
extern FUSEBMC_goal_t last_goal;
extern char * fuSeBMC_bitset_arr;
extern int fuSeBMC_env_goals_cnt;
extern FUSEBMC_goal_t fuSeBMC_bitset_sz_byte ;
void* fuSeBMC_alloc(uint32_t size);
void fuSeBMC_print_val_in_file (char * file_name , char * format, ...);
void fuSeBMC_log_error (char * format, ...);
void fuSeBMC_log_info (char * format, ...);
char * fuSeBMC_as_bits(void const * const ptr,size_t const size);
void fuSeBMC_setup_shm(void);
void fuSeBMC_init_mutex();
void fuSeBMC_init();
char fuSeBMC_generate_random_number_signed();
char fuSeBMC_generate_random_number_unsigned();
char * fuSeBMC_string2hexString(char* input);
char * fuSeBMC_generate_random_text(int length);
void fuSeBMC_reach_error();
// will inserted after return in main method.
void fuSeBMC_abort_prog();
ssize_t fuSeBMC_write(int __fd, const void *__buf, size_t __n);
ssize_t fuSeBMC_read(int __fd, void *__buf, size_t __nbytes);
void fuSeBMC___assert_fail (const char *__assertion, const char *__file,
				unsigned int __line, const char *__function);
void __VERIFIER_assume(int cond);
void __VERIFIER_error();
char __VERIFIER_nondet_char();
unsigned char __VERIFIER_nondet_uchar();
short __VERIFIER_nondet_short();
unsigned short __VERIFIER_nondet_ushort();
int __VERIFIER_nondet_int();
unsigned int __VERIFIER_nondet_uint();
long __VERIFIER_nondet_long();
unsigned long __VERIFIER_nondet_ulong();
long long __VERIFIER_nondet_longlong();
unsigned long long __VERIFIER_nondet_ulonglong();
float __VERIFIER_nondet_float();
double __VERIFIER_nondet_double();
_Bool __VERIFIER_nondet_bool();
void *__VERIFIER_nondet_pointer();
unsigned int __VERIFIER_nondet_size_t();
unsigned char __VERIFIER_nondet_u8();
unsigned short __VERIFIER_nondet_u16();
unsigned int __VERIFIER_nondet_u32();
unsigned int __VERIFIER_nondet_U32();
unsigned char __VERIFIER_nondet_unsigned_char();
unsigned int __VERIFIER_nondet_unsigned();
const char *__VERIFIER_nondet_string();
void fuseGoalCalled(FUSEBMC_goal_t goal);
//void fuSeBMC_send_signal_to_fuzzer(int sig);
void fuSeBMC_copy_stdin();
void fuSeBMC_run_TC_gen();
void fuSeBMC_setup_signal_handlers();
void fuSeBMC_SIGUSR2(int sig);
void fuSeBMC_SIGSEGV(int sig);
void fuSeBMC_SIGABRT(int sig);
void fuSeBMC_SIGINT(int sig);
void fuSeBMC_SIGTERM(int sig);

#ifdef __cplusplus
}
#endif
#endif