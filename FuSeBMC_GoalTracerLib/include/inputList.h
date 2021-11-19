#ifndef INPUTLIST_H
#define INPUTLIST_H

#include <stddef.h>
#include "inputTypes.h"

#ifdef __cplusplus
extern "C" {
#endif


/********* List FOR INPUTS *********/
typedef struct _FuSeBMC_input_node
{
	fuSeBMC_InputType_t input_type;
	void * val_ptr;	
} FuSeBMC_input_node_t;



#define ELEMENTS_PER_BUCKET 1000

extern int buckets_total_size;
extern int bucket_idx;
extern int elem_idx ;
extern FuSeBMC_input_node_t ** buckets_arr;

extern int fuSeBMC_NumOfInputsInTestcase;
//extern FuSeBMC_input_node_t * fuSeBMC_input_arr;
//extern int fuSeBMC_input_arr_count;


void fuSeBMC_create_input_list();
int fuSeBMC_get_sizeof_inputType(fuSeBMC_InputType_t input_type);
void * fuSeBMC_push_in_input_list(fuSeBMC_InputType_t input_type , void * val_ptr, size_t val_len);
void fuSeBMC_clear_input_list();

#ifdef __cplusplus
}
#endif
#endif /* INPUTLIST_H */