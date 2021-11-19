#include <stdio.h>
#include <limits.h>


int main() {
    // Write C code here
    _Bool b = (int)-200;
    if(b)
        printf("True");
    else
        printf("False");
    printf("\n\nHello world\n\n");
    if(-1)
    printf("-1 is True\n");
#ifdef __CHAR_UNSIGNED__
    printf( "%d\n", __CHAR_UNSIGNED__ );
#endif
    printf( "%d\n", CHAR_MAX);
    printf( "%d\n", CHAR_MIN);
    printf( "%hhd\n", CHAR_MAX);
    
    return 0;
}

