// not Compile.
int main()
{
     volatile unsigned long long a = 3;
      switch(8UL)
      {
         case 1UL:
GOAL_1:;

            //lbl:;
            __asm__ ("movb %%gs:%1,%0": "=q" (a): "m" (a));
            a++;
      }
    return 0;
}
