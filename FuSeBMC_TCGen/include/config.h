#ifndef CONFIG_H
#define CONFIG_H

#ifdef __cplusplus
extern "C" {
#endif

#define DEBUG
//#define STAND_ALONE
//#define FUSEBMC_EXPORT_AS_BITS
#define FUSEBMC_USE_BITSET

typedef int  FUSEBMC_goal_t;
#define FUSEBMC_goal_format "%d"

#define FUSEBMC_USE_THREAD_LOCK 0
#if FUSEBMC_USE_THREAD_LOCK
	
#else
	#define pthread_mutex_unlock(lock)
	#define pthread_mutex_lock(lock)
#endif

#ifdef __cplusplus
}
#endif

#endif /* CONFIG_H */

