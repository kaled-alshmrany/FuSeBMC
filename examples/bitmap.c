#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define IS_BIT_SET(goal) (fuSeBMC_bitset_arr[goal/8] & (char)(1<<(goal%8)))
//gcc -m32 -o bitmap.exe bitmap.c && ./bitmap.exe
unsigned char * fuSeBMC_bitset_arr = NULL;
unsigned char isBitSet(unsigned int goal)
{
	int bytePos = goal / (sizeof(char) * 8);
	int bitPos = goal % (sizeof(char) * 8);
	return ((fuSeBMC_bitset_arr[bytePos]) & ((unsigned char)(UINT8_C(1)<<bitPos)));
}
void setBit(unsigned int goal)
{
	int bytePos = goal / (sizeof(char) * 8);
	int bitPos = goal % (sizeof(char) * 8);
	fuSeBMC_bitset_arr[bytePos] |= ((unsigned char)(UINT8_C(1) << bitPos));
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
#define SIZE 100
int main()
{
	
	fuSeBMC_bitset_arr = malloc(SIZE);
	//setBit(1);
	//setBit(2);
	for(unsigned int i =0; i< SIZE * 8 -1; i++ )
		if(i%8 ==0) setBit(i);
	
	for(unsigned int i =0; i< SIZE * 8 -1; i++ )
		if(isBitSet(i)==UINT8_C(0))
			printf("Bit= %u is ZERO\n",i);
		else
			printf("Bit= %u iNOOOOOOOOOOOOOOOOOOOOO\n",i);
	/*if((fuSeBMC_bitset_arr[5/8] & (char)(1<<(5%8))) ==0)
		printf("Zero\n");
	else
		printf("Not Zero\n");
	printf("%hhd\n", (fuSeBMC_bitset_arr[5/8] & (char)(1<<(5%8))));
	*/
	printf("%s\n",fuSeBMC_as_bits(fuSeBMC_bitset_arr,SIZE));
	return 0;
}