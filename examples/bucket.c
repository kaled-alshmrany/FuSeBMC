#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

//gcc -o bucket bucket.c && ./bucket
typedef struct 
{
	int val1;
	int val2;
} node;

#define ELEMENTS_PER_BUCKET 5
int buckets_total_size = 10;
int bucket_idx = -1;
int elem_idx = ELEMENTS_PER_BUCKET -1; // previous Buckets are full.
node ** buckets_arr = NULL;

void push(int v1, int v2)
{
	

	if(elem_idx == ELEMENTS_PER_BUCKET -1) // Bucket is full
	{
		if(bucket_idx == buckets_total_size-1) // no more free buckets
		{
			//resize

			int buckets_total_size_old = buckets_total_size;
			buckets_total_size += 2;
			printf(" \n***resizing to buckets_total_size=%d\n\n",buckets_total_size);
			node ** tmp = buckets_arr;
			// create new array.
			node ** buckets_arr_new = malloc(buckets_total_size * sizeof(node *));


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
			if(!buckets_arr[bucket_idx])
			{
				printf("creating bucket_idx=%d\n",bucket_idx);
				buckets_arr[bucket_idx] = malloc(ELEMENTS_PER_BUCKET * sizeof(node));
			}
			else
			{
				printf("bucket_idx=%d is already allocated\n",bucket_idx);
			}
		}
		else // there is free bucket.
		{
			bucket_idx ++;
			elem_idx=0;
			if(!buckets_arr[bucket_idx])
			{
				printf("creating bucket_idx=%d\n",bucket_idx);
				buckets_arr[bucket_idx] = malloc(ELEMENTS_PER_BUCKET * sizeof(node));
			}
		}
	}
	else // current Bucket is not full
	{
		elem_idx++;
	}


	printf("inserting in bucket_idx=%d, elem_idx=%d\n", bucket_idx,elem_idx);
	buckets_arr[bucket_idx][elem_idx].val1 = v1;
	buckets_arr[bucket_idx][elem_idx].val2 = v2;
}

void pprint()
{
	for(int b = 0; b <= bucket_idx; b++)
	{
		int idx = (b==bucket_idx)?elem_idx : ELEMENTS_PER_BUCKET - 1;
		for(int e=0; e<=idx; e++)
			printf("buckets_arr[%d][%d]=(%d,%d)\n",b,e,buckets_arr[b][e].val1, buckets_arr[b][e].val2);
	}
}
void cclear()
{
	for(int b = 0; b <= bucket_idx; b++)
	{
		if(b !=0)
		{
			free(buckets_arr[b]);
			buckets_arr[b] = NULL;
		}
	}
	bucket_idx = -1;
	elem_idx = ELEMENTS_PER_BUCKET -1;
}
int main(int argc, char *argv[])
{
	buckets_arr = malloc(buckets_total_size * sizeof(node *));
	//for(int i=0; i< buckets_total_count; i++)
	//	buckets_arr[i] = malloc(ELEMENTS_PER_BUCKET * sizeof(node));
	
	for(int i=0; i< 50; i++)
		push(i,i);
	
	printf("*************************************\n");
	pprint();
	cclear();
	for(int i=100; i< 200; i++)
		push(i,i);
	printf("*************************************\n");
	pprint();
	return 0;
}