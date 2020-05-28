# 1 "/home/kaled/sdb1/my_instrument/examples/err.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 31 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 32 "<command-line>" 2
# 1 "/home/kaled/sdb1/my_instrument/examples/err.c"
extern void abort(void);
void reach_error(){int f;}
extern int __VERIFIER_nondet_int(void);

int N;
int ok(x)
{
    return x>0 && x<100 ;
}
int main ()
{

 N=100;
 int x[10];
 for (int i = 0; i < N; i++) {
    x[i] = __VERIFIER_nondet_int();
  }

    if(ok(x[2])&& ok(x[90]) && x[2]+x[90]==13){
      {reach_error();abort();}
    }

  return 1;
}
