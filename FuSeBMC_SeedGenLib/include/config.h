#ifndef CONFIG_H
#define CONFIG_H

#ifdef __cplusplus
extern "C" {
#endif

//between 0 and 127
#define FUSEBMC_MAX_RANDOM 4
#define FUSEBMC_MIN_RANDOM 0

// 0 disabled, 1 Enabled
#define FUSEBMC_GENERATE_POSITIV_AND_NEGATIV 0
#define FUSEBMC_GENERATE_INPUT_INFO 0

#define FUSEBMC_MAX_SEED_SIZE 2000000 
#define FUSEBMC_MAX_STRING_SIZE 100
#define FUSEBMC_MIN_STRING_SIZE 1
	
#define SEED_FILE_NAME_RANDOM_PART_LENGTH 20
#define FUSEBMC_FUZZER_SELECTIVE_INPUTS_FILE  "./selective_inputs.txt"
#define FuSEBMC_SELECTIVE_INPUTS_MAX_COUNT 100
#define FuSEBMC_IS_SELECTIVE_INPUTS_FROM_MAIN 99

#ifdef __cplusplus
}
#endif

#endif /* CONFIG_H */