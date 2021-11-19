#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/time.h>
#include <unistd.h>

//gcc -o set_time.exe set_time.c &&./set_time.exe
void fuSeBMC_SIGALRM(int sig)
{
	printf("void fuSeBMC_SIGALRM();\n");
	exit(0);
}
int main()
{
	struct sigaction sa;
	sa.sa_handler = NULL;
	sa.sa_flags = SA_RESTART;
	sa.sa_sigaction = NULL;
	sigemptyset(&sa.sa_mask);
	
	sa.sa_handler = fuSeBMC_SIGALRM;
	sigaction(SIGALRM, &sa, NULL);
	
	struct itimerval it;
	it.it_value.tv_sec = 3; // seconds
	//it.it_value.tv_usec = (timeout % 1000) * 1000;
	setitimer(ITIMER_REAL, &it, NULL);
	while(1)
	{
		sleep(1);
	}
	return 0;
}