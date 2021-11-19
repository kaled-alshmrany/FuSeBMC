// https://www.learn-c.org/en/Linked_lists
// https://www.tutorialspoint.com/data_structures_algorithms/linked_list_program_in_c.htm
#include <inputList.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#include <config.h>
#include <inputTypes.h>
#include <inputList.h>

#ifdef __cplusplus
extern "C" {
#endif
//FuSeBMC_input_node_t * fuSeBMC_input_arr = NULL;
//int fuSeBMC_input_arr_count = 0;



void* fuSeBMC_alloc(uint32_t size)
{
	if(size ==0)
	{
		fuSeBMC_log_error("cannot allocate size=%u\n",size);
		exit(-1);
	}
	void * ptr = malloc(size);
	if(!ptr)
	{
		fuSeBMC_log_error("ptr is NULL\n");
		exit(-1);
	}
	memset(ptr, 0, size);
	return ptr;
}
/**********************/
int buckets_total_size = 200;
int bucket_idx = -1;
int elem_idx = ELEMENTS_PER_BUCKET -1; // previous Buckets are full.
FuSeBMC_input_node_t ** buckets_arr = NULL;

static unsigned int fuSeBMC_num_of_inputs = 0;

#ifdef ARCH32

#endif
#ifdef ARCH64

#endif
/********* InputList FOR INPUTS *********/
size_t fuSeBMC_get_sizeof_inputType(fuSeBMC_InputType_t input_type)
{
	if(input_type == _char) return sizeof(signed char);
	if(input_type == _uchar) return sizeof(unsigned char);
	if(input_type == _short) return sizeof(signed short);
	if(input_type == _ushort) return sizeof(unsigned short);
	if(input_type == _int) return sizeof(signed int);
	if(input_type == _uint) return sizeof(unsigned int);
	if(input_type == _long) return sizeof(long);
	if(input_type == _ulong) return sizeof(unsigned long); 
	if(input_type == _longlong ) return sizeof(long long);
	if(input_type == _ulonglong ) return sizeof(unsigned long long);
	if(input_type == _float ) return sizeof(float);
	if(input_type == _double) return sizeof(double);
	if(input_type == _bool ) return sizeof(_Bool);
	if(input_type == _string )
	{
		fuSeBMC_log_error("fuSeBMC_get_sizeof_inputType in not valid for string");
		return sizeof(10); // TODO:
	}
	fuSeBMC_log_error("unknown type...");
	return -1 ;
	/*
	if(input_type == _char) return sizeof(signed char);
	if(input_type == _uchar) return sizeof(unsigned char);
	if(input_type == _short) return sizeof(signed short);
	if(input_type == _ushort) return sizeof(unsigned short);
#ifdef ARCH32
	if(input_type == _int) return 32 / 8;
	if(input_type == _uint) return 32 / 8;
#endif
#ifdef ARCH64
	if(input_type == _int) return 32 / 8;
	if(input_type == _uint) return 32 / 8;
#endif
	
#ifdef ARCH32
	if(input_type == _long) return 32/8;
	if(input_type == _ulong) return 32/8;
#endif
#ifdef ARCH64
	if(input_type == _long) return 64/8;
	if(input_type == _ulong) return 64/8;
#endif

	if(input_type == _longlong ) return sizeof(long long);
	if(input_type == _ulonglong ) return sizeof(unsigned long long);
	
	if(input_type == _float ) return sizeof(float);
	if(input_type == _double) return sizeof(double);
	if(input_type == _bool ) return sizeof(_Bool);
	if(input_type == _string ) return sizeof(10); // TODO:
	return -1 ;
*/
}
void fuSeBMC_create_input_list()
{
	if(buckets_arr == NULL)
	{
		buckets_arr = malloc(buckets_total_size * sizeof(FuSeBMC_input_node_t *));
		for(int b=0; b<buckets_total_size;b++)
			buckets_arr[b] = NULL;
		buckets_arr[0] = malloc(ELEMENTS_PER_BUCKET * sizeof(FuSeBMC_input_node_t));
	}
}

void * fuSeBMC_push_in_input_list(fuSeBMC_InputType_t input_type , void * val_ptr, size_t val_len)
{
	//return;
	//int input_size;
	/*if(input_type == _string)
		val_len = strlen(val_ptr);
	else
		val_len = fuSeBMC_get_sizeof_inputType(input_type);
	*/
	fuSeBMC_num_of_inputs ++;
	if(fuSeBMC_num_of_inputs > FUSEBMC_MAX_INPUTS_IN_ONE_TESTCASE)
		exit(0);
	if(elem_idx == ELEMENTS_PER_BUCKET -1) // Bucket is full
	{
		if(bucket_idx == buckets_total_size-1) // no more free buckets
		{
			//resize
			int buckets_total_size_old = buckets_total_size;
			buckets_total_size += 10;
			//printf("resizing to buckets_total_size=%d\n",buckets_total_size);
			FuSeBMC_input_node_t ** tmp = buckets_arr;
			// create new array.
			FuSeBMC_input_node_t ** buckets_arr_new = malloc(buckets_total_size * sizeof(FuSeBMC_input_node_t *));


			//copy old elements.
			for(int i = 0 ; i< buckets_total_size_old;i++)
				buckets_arr_new[i] = buckets_arr[i];
			for(int i = buckets_total_size_old ; i< buckets_total_size;i++)
				buckets_arr_new[i] = NULL;

			buckets_arr = buckets_arr_new;

			// free old array
			free(tmp);

			elem_idx = 0;
			bucket_idx++;
			if(buckets_arr[bucket_idx]== NULL)
			{
				buckets_arr[bucket_idx] = malloc(ELEMENTS_PER_BUCKET * sizeof(FuSeBMC_input_node_t));
			}
		}
		else // there is free bucket.
		{
			bucket_idx ++;
			elem_idx=0;
			if(buckets_arr[bucket_idx] == NULL)
			{
				buckets_arr[bucket_idx] = malloc(ELEMENTS_PER_BUCKET * sizeof(FuSeBMC_input_node_t));
			}
		}
	}
	else // current Bucket is not full
	{
		elem_idx++;
	}


	//printf("inserting in bucket_idx=%d, elem_idx=%d\n", bucket_idx,elem_idx);
	buckets_arr[bucket_idx][elem_idx].input_type = input_type;
	buckets_arr[bucket_idx][elem_idx].val_ptr = malloc(val_len);
	if(val_ptr != NULL)
		memcpy(buckets_arr[bucket_idx][elem_idx].val_ptr, val_ptr, val_len);
	return buckets_arr[bucket_idx][elem_idx].val_ptr;
	
}

void fuSeBMC_clear_input_list()
{
	if(bucket_idx < 0) return;
	for(int b = 0; b <= bucket_idx; b++)
	{
		int idx = (b==bucket_idx)?elem_idx : ELEMENTS_PER_BUCKET - 1;
		for(int e=0; e<=idx; e++)
		{
			free(buckets_arr[b][e].val_ptr);
			buckets_arr[b][e].val_ptr = NULL;
			buckets_arr[b][e].input_type = 0;
		}
		
		// let the first one allocated.
		if(b != 0 && buckets_arr[b] != NULL)
		{
			free(buckets_arr[b]);
			buckets_arr[b] = NULL;
		}
	}
	
	bucket_idx = -1;
	elem_idx = ELEMENTS_PER_BUCKET -1;
	
}
#ifdef __cplusplus
}
#endif