#include <StdCFuncHandler.h>


std::vector<std::string> StdCFuncHandler::vctStdCFuncToSearchFor = 
{
"printf","vfprintf","malloc","free","sprintf","strchr","strcpy","strcat","sscanf",
"pthread_mutex_init","pthread_mutex_lock","pthread_mutex_unlock","access","fscanf",
"feof","srand","rand","memset","memcpy","snprintf","ftok","getenv","setenv","atoi",
"atol","shmget","shmat","getpid","getppid","strlen","sigemptyset","sigaction",
"setitimer","pipe","getrlimit","setrlimit","dup2","execv","close","wait","read",
"write","open","fopen","fclose","fseek","fread","exit","kill","fork","fileno","fseeko","sleep","fstat",
"stat","lstat","getopt","getopt_long", "vasprintf","strsep","getutent","_IO_getc"
};

StdCFuncHandler::StdCFuncHandler()
{
	
}
void StdCFuncHandler::addIfStdC_Func(std::string pFuncName)
{
	for(std::string & funcName : StdCFuncHandler::vctStdCFuncToSearchFor)
		if(funcName == pFuncName)
		{
			this->vctStdCFuncFound.push_back(pFuncName);
			//std::cout << "ADD FUNC: " << pFuncName << std::endl;
			return;
		}
}

StdCFuncHandler * stdCFuncHandler = nullptr;