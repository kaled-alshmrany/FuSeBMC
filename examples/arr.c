#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdbool.h>
#include <gnu/libc-version.h>
#include <float.h>

// gcc -m32 arr.c -o arr.exe && ./arr.exe

#define ARR_SIZE 10
int count = 0;
void print_arr(int * arr)
{
	for(int i=0; i < ARR_SIZE;i++)
	{
		printf("arr[%d]=%d\n", i, arr[i]);
	}
}
void insert(int * arr, int key)
{
	register int i;
	int p;
	/* Determine the position where the new value will be insert.*/
   for(i=0;i<ARR_SIZE;i++)
     if(key<arr[i] || arr[i] == 0)
     {
       p = i;
       break;
     }
	printf("p=%d\n", p);
    /* move all data at right side of the array */
	count++;
   for(i=count-1;i>=p;i--)arr[i]= arr[i-1];
    /* insert value at the proper position */
    arr[p]=key;
	
}
int binary_search(int A[], int key, int len)
{
	int low = 0;
	int high = len -1;

  while (low <= high) {
    int mid = low + ((high - low) / 2);

    if (A[mid] == key) {
      return mid;
    }

    if (key < A[mid]) {
      high = mid - 1;
    }
    else {
      low = mid + 1;
    }
  }
  return -1;
}
char * fuSeBMC_as_bits(void const * const ptr,size_t const size)
{
	int bit_char_size = size * 8 + 1;
	char * bit_char = malloc(bit_char_size);
	char * bit_char_tmp = bit_char;
	memset(bit_char,'\0',bit_char_size);
	char *b = (char*) ptr;
	//unsigned char byte;
	//int i;
	
	for(size_t i=0; i< size;i++)
	{
		char byte = *b;
		 sprintf(bit_char_tmp,"%c%c%c%c%c%c%c%c",
				 				 
				(byte & 0x01 ? '1' : '0'),
				(byte & 0x02 ? '1' : '0'),
				(byte & 0x04 ? '1' : '0'),
				(byte & 0x08 ? '1' : '0'),
				(byte & 0x10 ? '1' : '0'),
				(byte & 0x20 ? '1' : '0'),
				(byte & 0x40 ? '1' : '0'), // 64 = 1000000				 
				(byte & 0x80 ? '1' : '0') // 128 =10000000				 
				 );
		b++;
		bit_char_tmp += 8;
	}
	
	/*for (i = size-1; i >= 0; i--)
	{
		for (j = 7; j >= 0; j--) 
		{
			byte = (b[i] >> j) & 1;
		sprintf (bit_char_tmp,"%u", byte);
			bit_char_tmp ++;
		}
	}*/
	return bit_char;
}
int isBitSet(void * ptr,int pos)
{
	int bytePos = 0;
	char bitPos = 0;
	if(pos != 0)
	{
		bytePos = pos / (sizeof(char) * 8);
		bitPos =  pos %  (sizeof(char) * 8);
	}
	char * tmpPtr = ptr + bytePos;
	char bit = (*tmpPtr >> bitPos) & (char)1;
	printf("pos=%d,bit=%d\n",pos, bit);
	return bit;
}
void setBit(void * ptr,int pos)
{
	int bytePos = 0;
	char bitPos = 0;
	if(pos != 0)
	{
		bytePos = pos / (sizeof(char) * 8);
		bitPos =  pos %  (sizeof(char) * 8);
	}
	char * tmpPtr = ptr + bytePos;
	*tmpPtr |= (char)1 << bitPos;
	printf("pos = %d ,  bytePos = %d,   bitPos=%d \n ",pos,bytePos,bitPos);
	
}
int main()
{
#define SIZE_BYTE 8
	
	for(int i=0; i<10;i++)
		printf("%d = [%s]\n",i, fuSeBMC_as_bits(&i,sizeof(i)));
	int size_bit = SIZE_BYTE * 8;
	void * pptr = malloc(SIZE_BYTE);
	memset(pptr,0,SIZE_BYTE);
	//for(int i=0;i<size_bit;i++)
	//	setBit(pptr,size_bit,i);
	isBitSet(pptr,0);
	setBit(pptr,0);isBitSet(pptr,0);
	setBit(pptr,0);
	setBit(pptr,7);isBitSet(pptr,7);
	setBit(pptr,10);isBitSet(pptr,10);
	setBit(pptr,size_bit-1);isBitSet(pptr,size_bit-1);
	printf("[%s]\n",fuSeBMC_as_bits(pptr,SIZE_BYTE));
	return 0;
	//float inp_f;
	//scanf("%f", &inp_f);
	//printf("result = %.20e\n",inp_f);
	
	float f = 333.123456789;
	printf("%.18e\n",f);
	printf("%.3e\n",f);
	printf("%.5e\n",f);
	printf("%.10e\n",f);
	printf("%f\n",f);
	exit(0);
	printf("%ld\n",__STDC_VERSION__);
	char b = 0b10000000;
	printf("binary as unsigned=%hhu\n",b); // %hhd -> char ; hhu unsigned
	printf("binary as signed=%hhd\n",b);
	_Bool val = (_Bool)788;
	printf("sizeof(_Bool)=%d\n",sizeof(_Bool));
    printf("i=%d\n",val);
	printf("i=%d\n",(int)val);
	printf("-------------------\n");
	_Bool fls = false;
	_Bool tru = true;
	char nzero = -0;
	printf("fls=%s\n",fuSeBMC_as_bits(&fls,sizeof(_Bool)));
	printf("tru=%s\n",fuSeBMC_as_bits(&tru,sizeof(_Bool)));
	printf("nzero=%s\n",fuSeBMC_as_bits(&nzero,sizeof(char)));
	
	char * ptr = malloc(sizeof(_Bool));
	//memcpy(ptr, &tru, sizeof(_Bool));
	memcpy(ptr, &tru, sizeof(_Bool));
	
	_Bool val_from_ptr = (_Bool)*((_Bool *)ptr);
	printf("fuSeBMC_as_bits=%s\n",fuSeBMC_as_bits(&val_from_ptr,sizeof(_Bool)));
	if(val_from_ptr == true) printf("val_from_ptr = true\n");
	else
		printf("val_from_ptr = false\n");
			

    return 0;
	int arr[ARR_SIZE];
	for(int i=0;i<ARR_SIZE;i++) arr[i] = +	0;
	print_arr(arr);
	printf("search for 100 =%d\n",binary_search(arr,100,count));
	printf("Inserting \n");
	insert(arr,10);
	insert(arr,5);
	insert(arr,6);
	print_arr(arr);
	printf("search for 1 =%d\n",binary_search(arr,1,count));
	printf("search for 0 =%d\n",binary_search(arr,0,count));
	printf("search for 10 =%d\n",binary_search(arr,10,count));
	printf("search for 5 =%d\n",binary_search(arr,5,count));
	printf("search for 6 =%d\n",binary_search(arr,6,count));
	return 0;
	

}

