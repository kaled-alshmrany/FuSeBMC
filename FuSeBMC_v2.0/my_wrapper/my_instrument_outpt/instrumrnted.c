extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_int(void);
void __VERIFIER_assert(int cond) { if(!(cond)) {
GOAL_1:;
 ERROR: __VERIFIER_error(); }
/*B_140_(1)*/

else
 {
GOAL_2:;
}
/*E_140_(1)*/
 }
struct S
{
 int n;
};
struct S s[100000];
int main()
{
 int i;
 int c;
 c = __VERIFIER_nondet_int();
 for(i = 0; i < 100000; i++)
 {
GOAL_3:;

  if(c > 5)
/*B_216_(2)*/

{

GOAL_4:;

/*E_216_(2)*/

   break;
/*B_219_(3)*/

/*B*/}
else 
{
GOAL_5:;
}
/*E_219_(3)*/

  s[i].n = 10;
 }
 for(i = 0; i < 100000; i++)
 {
GOAL_6:;

  if(c <= 5)
/*B_216_(4)*/

{

GOAL_7:;

/*E_216_(4)*/

   __VERIFIER_assert(s[i].n == 10);
/*B_219_(5)*/

/*B*/}
else 
{
GOAL_8:;
}
/*E_219_(5)*/

 }
 return 0;
}
