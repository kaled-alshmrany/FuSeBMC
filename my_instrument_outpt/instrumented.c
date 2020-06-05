extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_int();

void init_nondet(int x[10]) {
  int i;
  for (i = 0; i < 10; i++) {
GOAL_1:;

    x[i] = __VERIFIER_nondet_int();
  }
}

int rangesum (int x[10])
{
  int i;
  long long ret;
  ret = 0;
  int cnt = 0;
  for (i = 0; i < 10; i++) {
GOAL_2:;

    if( i > 10/2){
GOAL_3:;

       ret = ret + x[i];
       cnt = cnt + 1;
    }
/*B_143_(1)*/

else
 {
GOAL_4:;
}
/*E_143_(1)*/

  }
  if ( cnt !=0)
/*B_219_(2)*/

{

GOAL_5:;

/*E_222_(2)*/

    return ret / cnt;
  
/*B_232_(3)*/

/*A*/}

/*E_232_(3)*/
else
/*B_219_(4)*/

{

GOAL_6:;

/*E_222_(4)*/

    return 0;
/*B_232_(5)*/

/*B*/}

/*E_232_(5)*/

}

int main ()
{
  int x[10];
  init_nondet(x);
  int temp;
  int ret;
  int ret2;
  int ret5;

  ret = rangesum(x);

  temp=x[0];x[0] = x[1]; x[1] = temp;
  ret2 = rangesum(x);
  temp=x[0];
  for(int i =0 ; i<10 -1; i++){
GOAL_7:;

     x[i] = x[i+1];
  }
  x[10 -1] = temp;
  ret5 = rangesum(x);

  if(ret != ret2 || ret !=ret5){
GOAL_8:;

    __VERIFIER_error();
  }
/*B_143_(6)*/

else
 {
GOAL_9:;
}
/*E_143_(6)*/

  return 1;
}
