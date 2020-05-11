extern void __VERIFIER_error() __attribute__ ((__noreturn__));
void __VERIFIER_assert(int cond) {

GOAL_1:;
 if(!(cond)) {
GOAL_2:;
 ERROR: __VERIFIER_error(); } }
extern int __VERIFIER_nondet_int();

int insert( int set [] , int size , int value ) {

GOAL_3:;

  set[ size ] = value;
  return size + 1;
}
int elem_exists( int set [ ] , int size , int value ) {

GOAL_4:;

  int i;
  for ( i = 0 ; i < size ; i++ ) {
GOAL_5:;

    if ( set[ i ] == value ) 
{

GOAL_6:;
 return 0;
}

  }
  return 0;
}
int main( ) {

GOAL_7:;

  int n = 0;
  int set[ 100000 ];
  int x;
  int y;
	
	for (x = 0; x < 100000; x++)
	{
GOAL_8:;

	  set[x] = __VERIFIER_nondet_int();
	}
	
  for ( x = 0 ; x < n ; x++ ) {
GOAL_9:;

    for ( y = x + 1 ; y < n ; y++ ) {
GOAL_10:;

      __VERIFIER_assert( set[ x ] != set[ y ] );
    }
  }
  int values[ 100000 ];
  int v;
	
	for (v = 0; v < 100000; v++)
	{
GOAL_11:;

	  values[v] = __VERIFIER_nondet_int();
	}
	
  for ( v = 0 ; v < 100000 ; v++ ) {
GOAL_12:;

    if ( !elem_exists( set , n , values[ v ] ) ) {
GOAL_13:;

      n = insert( set , n , values[ v ] );
    }
  }
  for ( x = 0 ; x < n ; x++ ) {
GOAL_14:;

    for ( y = x + 1 ; y < n ; y++ ) {
GOAL_15:;

      __VERIFIER_assert( set[ x ] != set[ y ] );
    }
  }
  return 0;
}
