#ifndef INPUTLIST_H
#define INPUTLIST_H

#include <stddef.h>
#include <stdint.h>
#include "inputTypes.h"

#ifdef __cplusplus
extern "C" {
#endif

void fuSeBMC_print_val_in_file (char * file_name , char * format, ...);
void fuSeBMC_log_error (char * format, ...);
void fuSeBMC_log_info (char * format, ...);

typedef uint32_t u32;
typedef uint8_t  u8;

/********* List FOR INPUTS *********/
typedef struct _FuSeBMC_input_node
{
	fuSeBMC_InputType_t input_type;
	void * val_ptr;
} FuSeBMC_input_node_t;



#define ELEMENTS_PER_BUCKET 1000
#define FUSEBMC_MAX_INPUTS_IN_ONE_TESTCASE (1000000 + 1)

extern int buckets_total_size;
extern int bucket_idx;
extern int elem_idx ;
extern FuSeBMC_input_node_t ** buckets_arr;

extern FuSeBMC_input_node_t * fuSeBMC_input_arr;
extern int fuSeBMC_input_arr_count;


void fuSeBMC_create_input_list();
size_t fuSeBMC_get_sizeof_inputType(fuSeBMC_InputType_t input_type);
void * fuSeBMC_push_in_input_list(fuSeBMC_InputType_t input_type , void * val_ptr, size_t val_len);
void fuSeBMC_clear_input_list();

#ifdef __cplusplus
}
#endif
#endif /* INPUTLIST_H */