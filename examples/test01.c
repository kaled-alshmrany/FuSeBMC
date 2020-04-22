extern char __VERIFIER_nondet_char(void);
extern void abort();
extern void reach_error();
extern void __VERIFIER_error();
extern unsigned int __VERIFIER_nondet_int(void);
void __VERIFIER_assert(int cond) {
  if (!(cond)) {
    ERROR: {
    reach_error();
    //abort();
    }
  }
  return;
}

int main()
{
	int x=__VERIFIER_nondet_int();
	int y=__VERIFIER_nondet_int();
	__VERIFIER_assert(x>0);
	__VERIFIER_assert(y>0);
	__VERIFIER_assert(x+y==37);
	if(x<20&&x>17)
	{
		if(y<20&&y>16)
		{
			int z=x+y;
			//printf("SSS=%d\n",z);
			if(z==37)
				__VERIFIER_error();
		}
	}
	return 0;
	
}

/*
bin/condtest --spec tool_templates/coverage-branches.prp --testers cpa-tiger,coveritest,klee --timelimit-testers 300 --no-cycle bin/test01.c
*/
