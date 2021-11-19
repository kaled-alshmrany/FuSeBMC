#ifndef GOALLIST_H
#define GOALLIST_H

#include <config.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

extern int fuSeBMC_env_goals_cnt;
extern char * fuSeBMC_bitset_arr;
extern char * fuSeBMC_run_id;



typedef struct
{
	FUSEBMC_goal_t  goal;
} FuSeBMC_goal_node_t;

#define alloc_printf(_str...)({\
	char * _tmp; \
	int32_t _len = snprintf(NULL, 0, _str);\
	if (_len < 0) {fuSeBMC_log_error("Whoa, snprintf() fails?!");exit(0);}\
	_tmp = malloc(_len + 1);\
	snprintf((char*)_tmp, _len + 1, _str);\
	_tmp;\
	})
void fuSeBMC_create_goal_list();
void fuSeBMC_push_in_goal_list(FUSEBMC_goal_t goal);
int fuSeBMC_find_in_goal_list(FUSEBMC_goal_t goal);

extern void fuSeBMC_log_error (char * format, ...);
void* fuSeBMC_alloc(uint32_t size);

#ifdef __cplusplus
}
#endif

#endif /* GOALLIST_H */