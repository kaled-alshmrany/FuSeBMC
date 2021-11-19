#ifndef FUSEBMC_GOALTRACERLIB_H
#define FUSEBMC_GOALTRACERLIB_H

#include "goalList.h"

#ifdef __cplusplus
extern "C" {
#endif
void fuSeBMC_init();
void fuSeBMC_init_mutex();
void fuseGoalCalled(FUSEBMC_goal_t goal);

#ifdef __cplusplus
}
#endif
#endif

