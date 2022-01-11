#ifndef CONFIG_H
#define CONFIG_H

#ifdef __cplusplus
extern "C" {
#endif
#define TRACER_EXPORT_TESTCASE
#define TRACER_MAX_NUM_IN_TESTCASE 100000
#define DEBUG
//#define FUSEBMC_EXPORT_AS_BITS
#define FUSEBMC_USE_BITSET
#define TRACER_TESTCASE_FILENAME "./tracer_testcase.txt"
typedef int  FUSEBMC_goal_t;
#define FUSEBMC_goal_format "%d"

#define FUSEBMC_USE_THREAD_LOCK 1
#if FUSEBMC_USE_THREAD_LOCK
	
#else
	#define pthread_mutex_unlock(lock)
	#define pthread_mutex_lock(lock)
#endif

#ifdef __cplusplus
}
#endif

#endif /* CONFIG_H */

