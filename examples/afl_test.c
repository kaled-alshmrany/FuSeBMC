//char * fuSeBMC_run_id = "aaaaaa";
//int fuSeBMC_category = 2;
extern int __VERIFIER_nondet_int(void);
void reach_error()
{
	
}
int main()
{
	int a = __VERIFIER_nondet_int();
	int b = __VERIFIER_nondet_int();
	if(a>0 && b >0 && a <100 && b <100 && a+b ==30)
		reach_error();
}