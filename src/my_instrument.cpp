#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <cstdlib>
#include <vector>
#include <system_error>

#include "llvm/Support/Host.h"
#include <llvm/Support/raw_ostream.h>
#include "llvm/ADT/IntrusiveRefCntPtr.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/FileSystem.h"

#include "clang/Basic/DiagnosticOptions.h"
#include "clang/Frontend/TextDiagnosticPrinter.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Basic/TargetOptions.h"
#include "clang/Basic/TargetInfo.h"
#include "clang/Basic/FileManager.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Lex/Lexer.h"
#include "clang/Basic/Diagnostic.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/Parse/ParseAST.h"
#include "clang/Rewrite/Frontend/Rewriters.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include <clang/Lex/PreprocessorOptions.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Basic/Builtins.h>
#include <llvm/Support/Path.h>

#include <my_instrument.h>
#include <MyVisitor.h>
#include <TestVisitor.h>
#include <MyHolder.h>
#include <GoalCounter.h>
#include <MyOptions.h>
#include <iostream>
#include <fstream>



using namespace clang;

bool MustPrintGeneratedCode = false;
MyOptions * myOptions;
class MyASTConsumer:public ASTConsumer
{
 public:
     MyASTConsumer(Rewriter &Rewrite,MyHolder& H) : rv(Rewrite,H),TheHolder(H) { }
     virtual bool HandleTopLevelDecl(DeclGroupRef d);
     MyVisitor rv;
     MyHolder& TheHolder;
};

bool MyASTConsumer::HandleTopLevelDecl(DeclGroupRef d)
{
  typedef DeclGroupRef::iterator iter;
  for (iter b = d.begin(), e = d.end(); b != e; ++b)
  {
    rv.TraverseDecl(*b);
  }

  return true; // keep going
}
/***/
/*class MyASTConsumer2:public ASTConsumer
{
 public:
     MyASTConsumer2(Rewriter &Rewrite,MyHolder& H) : rv(Rewrite,H),TheHolder(H) { }
     virtual bool HandleTopLevelDecl(DeclGroupRef d);
     TestVisitor rv;
     MyHolder& TheHolder;
};
 
bool MyASTConsumer2::HandleTopLevelDecl(DeclGroupRef d)
{
  typedef DeclGroupRef::iterator iter;
  for (iter b = d.begin(), e = d.end(); b != e; ++b)
  {
    rv.TraverseDecl(*b);
  }

  return true; // keep going
}*/
/**/
void usage(char * prog)
{
    std::cout << prog <<" --input inp --output outpt [-h|--help] [--goal-output-file file] [--show-parse-tree] "<<std::endl;
    std::cout <<"\t\t\t\t [--goal-pro-func-output-dir dir] [--add-else] [--add-labels] [--add-goal-at-end-of-func] " << std::endl;
    std::cout<<"\t\t\t\t[--add-label-in-func lbl_func pairs] [--compiler-args][..][..]"<<std::endl;
    std::cout << "--help|-h\t\tShow the usage."<<std::endl;
    std::cout << "--input inp\t\tThe C input source file to be instrumented"<<std::endl;
    std::cout << "--output outpt\t\t The output file that will be created, includes the instrumented source code. "<<std::endl;
    std::cout << "--goal-output-file file\t\tThe Number of Generated Goals will be stored in this file."<<std::endl;
    std::cout << "--show-parse-tree\t\t Show the parse tree of the source code."<<std::endl;
    std::cout << "--goal-pro-func-output-dir dir\t\tFor each function in the source,It will be generated a file(same name of function)"<< std::endl;
    std::cout<<"\t\t\t\tthat includes the goals in  this function, these generated files will be stored in this directory."<<std::endl;
    std::cout << "--add-else\t\tAdd 'Else' statement if not exits."<<std::endl;
    std::cout << "--add-labels\t\tAdd labels in statements(if,else,while,for...)."<<std::endl;
    std::cout << "--add-goal-at-end-of-func\t\tA Goal will be added at the end of each function (or before 'return')"<<std::endl;    
    std::cout << "--add-label-in-func lbl_func pairs\t\tAdd one label in the corresponding function: lbl1=func1,lbl2=func2"<<std::endl;    
    std::cout << "--compiler-args\t\tThe next arguments will be passed to the compiler."<<std::endl;
    std::cout << "Example 1:" <<prog<<"--input mysource.c --output myout.c --goal-output-file theGoals.txt "<<std::endl;
    std::cout << "Example 2:" <<prog<<"--input mysource.c --output myout.c --goal-pro-func-output-dir /home/myout "<<std::endl;
    std::cout << "Example 3:" <<prog<<"--input mysource.c --output myout.c --compiler-args -I/user/include -I/home/dir1"<<std::endl;
}

std::vector<std::string> * split(std::string s,std::string del)
{
    std::vector<std::string> * vect = new std::vector<std::string>();
    size_t pos = 0;
    std::string token;
    while ((pos = s.find(del)) != std::string::npos)
    {
        token = s.substr(0, pos);
        vect->push_back(token);
        s.erase(0, pos + del.length());
    }
     vect->push_back(s);
    return vect;
}
int main(int argc, char **argv)
{

  myOptions = new MyOptions();
  int compilerArgsIndex=argc;
  for(int i=0;i<argc;i++)
  {
      if(strcmp(argv[i],"--compiler-args")==0)
      {
          if(compilerArgsIndex!=argc)
          {
              std::cerr << "duplicated argument: --compiler-args" << std::endl;
              usage(argv[0]);
              exit(-1);
              
          }
          else
              compilerArgsIndex=i;
      }
  }
  
  for(int i=0;i<compilerArgsIndex;i++)
  {
      if(strcmp(argv[i],"--help")==0 || strcmp(argv[i],"-h")==0)
      {
          usage(argv[0]);
          exit(0);
      }
  }
  int arg_index=1;  
  while(true)  
  {
      if(arg_index==compilerArgsIndex)break;
      char * the_arg=argv[arg_index];
      if(strcmp(the_arg,"--input")==0)
      {
          arg_index++;
          if(arg_index==compilerArgsIndex || argv[arg_index][0]=='-')
          {
              std::cerr << "No Input" << std::endl;
              usage(argv[0]);
              exit(-1);
          }          
          myOptions->inputFile =  argv[arg_index];
      }
      else if(strcmp(the_arg,"--output")==0)
      {
          arg_index++;
          if(arg_index==compilerArgsIndex || argv[arg_index][0]=='-')
          {
              std::cerr << "No Output" << std::endl;
              usage(argv[0]);
              exit(-1);
          }          
          myOptions->outputFile =  argv[arg_index];
      }
      else if(strcmp(the_arg,"--goal-output-file")==0)
      {
          arg_index++;
          if(arg_index==compilerArgsIndex || argv[arg_index][0]=='-')
          {
              std::cerr << "No goal-output-file" << std::endl;
              usage(argv[0]);
              exit(-1);
          }          
          myOptions->goalOutputFile =  argv[arg_index];
      }
      else if(strcmp(the_arg,"--show-parse-tree")==0)
      {
        myOptions->showParseTree=true;
      }
      else if(strcmp(the_arg,"--goal-pro-func-output-dir")==0)
      {
          arg_index++;
          if(arg_index==compilerArgsIndex || argv[arg_index][0]=='-')
          {
              std::cerr << "No goal-pro-func-output-dir" << std::endl;
              usage(argv[0]);
              exit(-1);
          }          
          myOptions->goalProFuncOutputDir =  argv[arg_index];
      }
      else if(strcmp(the_arg,"--add-else")==0)
      {
          myOptions->addElse = true;
      }
      else if(strcmp(the_arg,"--add-labels")==0)
      {
          myOptions->addLabels = true;
      }
      else if(strcmp(the_arg,"--add-goal-at-end-of-func")==0)
      {
          myOptions->addGoalAtEndOfFunc = true;
      }
      // 20.05.2020
      else if(strcmp(the_arg,"--add-label-in-func")==0)
      {
          myOptions->addLabelInFunc = true;
          arg_index++;
          if(arg_index==compilerArgsIndex || argv[arg_index][0]=='-')
          {
              std::cerr << "No value for :add-label-in-func" << std::endl;
              usage(argv[0]);
              exit(-1);
          }          
          
          std::vector<std::string> * lbl_func_pairs=split(argv[arg_index],",");
          for(std::string lbl_func_pair : *lbl_func_pairs)
          {
              std::vector<std::string> * lbl_func=split(lbl_func_pair,"=");
              assert(lbl_func->size()==2);
              myOptions->funcLabelMap[(*lbl_func)[1]]=(*lbl_func)[0];                      
              delete lbl_func;
          }
          delete lbl_func_pairs;
      }
      else 
      {
          std::cerr << "unknown option:" << the_arg << std::endl;
          usage(argv[0]);
          exit(-1);
      }
      arg_index++;
      
  }
#ifdef MYDEBUG
  std::cout <<"myOptions->inputFile=" << myOptions->inputFile << std::endl;
  std::cout <<"myOptions->outputFile=" << myOptions->outputFile << std::endl;
  std::cout <<"myOptions->goalOutputFile=" << myOptions->goalOutputFile << std::endl;
  std::cout <<"myOptions->goalProFuncOutputDir=" << myOptions->goalProFuncOutputDir << std::endl;
  std::cout <<"myOptions->addElse=" << myOptions->addElse << std::endl;
  std::cout <<"myOptions->addGoalAtEndOfFunc=" << myOptions->addGoalAtEndOfFunc << std::endl;
  std::cout <<"myOptions->showParseTree=" << myOptions->showParseTree << std::endl;
  std::cout <<"myOptions->addLabelInFunc=" << myOptions->addLabelInFunc << std::endl;
  for (auto const& map_elem : myOptions->funcLabelMap)
  {
      std::cout << map_elem.first  << ':' << map_elem.second << std::endl ;
  }
#endif
  if(myOptions->inputFile.empty())
  {
      std::cerr <<"No Input File "<< std::endl;
      usage(argv[0]);
      exit(-1);
  }
  
  // Make sure it exists
  struct stat sb;
  if (stat(myOptions->inputFile.c_str(), &sb) == -1)
  {
    std::cerr << "Cannot open file:" << myOptions->inputFile <<std::endl;
    exit(EXIT_FAILURE);
  }
  if(myOptions->outputFile.empty())
  {
      std::cerr << "No output File" <<std::endl;
      usage(argv[0]);
      exit(-1);
  }
  int new_args_count = argc - compilerArgsIndex + 1;
  char ** new_argv =(char**) malloc(sizeof(char *) * new_args_count);
  int j=0;
  for(int i = compilerArgsIndex+1; i<new_args_count;i++)
  {
      new_argv[j] = argv[i];
      j++;
  }
  new_argv[new_args_count-1] =const_cast<char *>(myOptions->inputFile.c_str()); 
  
  SmallVector<char,1024> path_vect;
  llvm::sys::fs::real_path(argv[0],path_vect,true);
  std::string current_folder = llvm::sys::path::parent_path(path_vect.data()).str();
  //std::cout << path_vect.data() << std::endl;
  //std::cout << llvm::sys::path::parent_path(path_vect.data()).str() << std::endl;
  
  /*argc=6;
  char *argvv[]={"./my_instrument", "./examples/a.cpp", "./examples/uftp_out.c" , "./examples/uftp_goals.txt",
  "./examples/goals_out", "-I/home/kaled/sdb1/uFTP/library", "-DOPENSSL_ENABLE"};
  argv=argvv;
  */
  
  
   /*std::string inputFile(argv[1]);
   std::string outputFile(argv[2]);
   std::string goalOutputFile(argv[3]);
   std::string goalProFuncDir(argv[4]);
   if(goalProFuncDir != "-nogoalProFunc") */
   GoalCounter::getInstance().mustGenerateFuncLabelMap=!myOptions->goalProFuncOutputDir.empty();
  //std::string fileName(argv[argc - 1]);
    
  
 

  CompilerInstance compiler;
  DiagnosticOptions diagnosticOptions;
  compiler.createDiagnostics();
  //compiler.createDiagnostics(argc, argv);
  
  /*for(int i=0;i<new_args_count;i++)
  {
      std::cout << i << "=" << new_argv[i] << std::endl;
  }*/
  
  // Create an invocation that passes any flags to preprocessor
  CompilerInvocation *Invocation = new CompilerInvocation;
  bool compile_result = CompilerInvocation::CreateFromArgs(*Invocation, new_argv, new_argv + new_args_count - 1, compiler.getDiagnostics());
  if(!compile_result)
  {
      llvm::errs() << "Cannot compile\n";
      //exit(-1);
  }
  compiler.setInvocation(std::shared_ptr<CompilerInvocation>(Invocation));

  // Set default target triple
    std::shared_ptr<clang::TargetOptions> pto = std::make_shared<clang::TargetOptions>();
  pto->Triple = llvm::sys::getDefaultTargetTriple();
    TargetInfo *pti = TargetInfo::CreateTargetInfo(compiler.getDiagnostics(), pto);
  compiler.setTarget(pti);

  compiler.createFileManager();
  compiler.createSourceManager(compiler.getFileManager());

  HeaderSearchOptions &headerSearchOptions = compiler.getHeaderSearchOpts();

  // <Warning!!> -- Platform Specific Code lives here
  // This depends on A) that you're running linux and
  // B) that you have the same GCC LIBs installed that
  // I do.
  // Search through Clang itself for something like this,
  // go on, you won't find it. The reason why is Clang
  // has its own versions of std* which are installed under
  // /usr/local/lib/clang/<version>/include/
  // See somewhere around Driver.cpp:77 to see Clang adding
  // its version of the headers to its include path.
  // To see what include paths need to be here, try
  // clang -v -c test.c
  // or clang++ for C++ paths as used below:
  /*headerSearchOptions.AddPath("/usr/include/c++/4.6",clang::frontend::Angled,false,false);
  headerSearchOptions.AddPath("/usr/include/c++/4.6/i686-linux-gnu",clang::frontend::Angled,false,false);
  headerSearchOptions.AddPath("/usr/include/c++/4.6/backward",clang::frontend::Angled,false,false);
  headerSearchOptions.AddPath("/usr/local/include",clang::frontend::Angled,false,false);
  headerSearchOptions.AddPath("/usr/local/lib/clang/3.3/include",clang::frontend::Angled,false,false);
  headerSearchOptions.AddPath("/usr/include/i386-linux-gnu",clang::frontend::Angled,false,false);
  headerSearchOptions.AddPath("/usr/include",clang::frontend::Angled,false,false);
  */
  std::ifstream includesFile;
  includesFile.open(current_folder + "/myincludes.txt");
  if (includesFile)
  { 
      std::string line;
      while (std::getline(includesFile,line))
      {
          //std::cout << line << std::endl;
          headerSearchOptions.AddPath(line,clang::frontend::Angled, false, false);
      }
      includesFile.close();      
  }
  //return 0;
   
  //headerSearchOptions.AddPath(std::string("/home/kaled/clang_base/lib/clang/6.0.0/include"), clang::frontend::Angled, false, false);
  //headerSearchOptions.AddPath(std::string("/usr/include"),clang::frontend::Angled, false, false);
  //headerSearchOptions.AddPath(std::string("/usr/include/linux"), clang::frontend::Angled, false, false);
  //headerSearchOptions.AddPath(std::string("/usr/include/c++/9/tr1"), clang::frontend::Angled, false, false);
  //headerSearchOptions.AddPath(std::string("/usr/include/c++/9"), clang::frontend::Angled, false, false);
  //headerSearchOptions.AddPath(std::string("/home/kaled/sdb1/uFTP/library"), clang::frontend::Angled,false,false);
    
  // </Warning!!> -- End of Platform Specific Code


  // Allow C++ code to get rewritten
  LangOptions langOpts;
  langOpts.GNUMode = 1; 
  langOpts.CXXExceptions = 1; 
  langOpts.RTTI = 1; 
  langOpts.Bool = 1; 
  langOpts.CPlusPlus = 1;
  
  langOpts.WChar = true;
  langOpts.Blocks = true;
  langOpts.DebuggerSupport = true;
  //langOpts.SpellChecking = false;
  //langOpts.ThreadsafeStatics = false;
  //langOpts.AccessControl = false;
  langOpts.DollarIdents = true;
  langOpts.Exceptions = true;
  
  //langOpts.NoBuiltin=false;  
  
 
  compiler.createPreprocessor(clang::TU_Complete);
  compiler.getPreprocessorOpts().UsePredefines = true;
  compiler.createASTContext();
  Preprocessor & preprocessor = compiler.getPreprocessor();
  Invocation->setLangDefaults(langOpts, clang::InputKind::CXX,compiler.getTarget().getTriple(),compiler.getPreprocessorOpts(), clang::LangStandard::lang_c11); 
  preprocessor.SetSuppressIncludeNotFoundError(false);
  preprocessor.getBuiltinInfo().initializeBuiltins(preprocessor.getIdentifierTable(),preprocessor.getLangOpts());
  
  // Initialize rewriter
  Rewriter Rewrite;
  Rewrite.setSourceMgr(compiler.getSourceManager(),compiler.getLangOpts());

  const FileEntry *pFile = compiler.getFileManager().getFile(myOptions->inputFile);
  compiler.getSourceManager().setMainFileID( compiler.getSourceManager().createFileID( pFile, clang::SourceLocation(), clang::SrcMgr::C_User));
  compiler.getDiagnosticClient().BeginSourceFile(compiler.getLangOpts(),&compiler.getPreprocessor());
  MyHolder myHolder;
  myHolder.SourceManager = &compiler.getSourceManager();
  myHolder.ASTContext = &compiler.getASTContext();
  if(preprocessor.hadModuleLoaderFatalFailure())
  {
      std::cout << "ERRRORRRRR" << std::endl;
      exit(-1);
  }
  MyASTConsumer astConsumer(Rewrite,myHolder);
  //MyASTConsumer2 astConsumer(Rewrite,myHolder);

  // Convert <file>.c to <file_out>.c
  /*std::string outName (fileName);
  size_t ext = outName.rfind(".");
  if (ext == std::string::npos)
     ext = outName.length();
  outName.insert(ext, "_out");
   */
  
  std::error_code OutErrorInfo;
  std::error_code ok;
  llvm::raw_fd_ostream outFile(llvm::StringRef(myOptions->outputFile), OutErrorInfo, llvm::sys::fs::F_None);
  

  if (OutErrorInfo == ok)
  {
    // Parse the AST
    clang::ParseAST(compiler.getPreprocessor(), &astConsumer, compiler.getASTContext());
    compiler.getDiagnosticClient().EndSourceFile();

    // Now output rewritten source code
    clang::FileID fileID =compiler.getSourceManager().getMainFileID();
    if(fileID.isInvalid())
    {
        llvm::errs() << "File ID is not valid.\n";
        exit(-1);
    }
    
    const RewriteBuffer *RewriteBuf = Rewrite.getRewriteBufferFor(fileID);
    if(RewriteBuf)
    {
        std::cout << "Output to: " << myOptions->outputFile << std::endl;
       outFile << std::string(RewriteBuf->begin(), RewriteBuf->end());
        if(MustPrintGeneratedCode)
            llvm::outs() << std::string(RewriteBuf->begin(), RewriteBuf->end());
    }
    else
    {
        llvm::errs() << "No changes can be made.\n";
        llvm::errs() << "The input file will be copied to the output file.\n";
        // copy the input file to the output
        std::ifstream inputFilefs;
        inputFilefs.open(myOptions->inputFile);
        if (inputFilefs)
        { 
            std::string line;
            while (std::getline(inputFilefs,line))
            {
                outFile << line << "\n";
            }
            inputFilefs.close();
        }
    }
  }
  else
  {
    llvm::errs() << "Cannot open " << myOptions->outputFile << " for writing\n";
  }

  outFile.close();
 #ifdef MYDEBUG
  //system(("sed -i '/^$/d' "+myOptions->outputFile).c_str());
#endif
  /***********/
  std::cout << "We have: " << GoalCounter::getInstance().counter << " Goals." << std::endl;
  if(!myOptions->goalOutputFile.empty())
  {
    std::cout << "Output Goals to: " << myOptions->goalOutputFile << std::endl;
    llvm::raw_fd_ostream goalOutputFile_fs(llvm::StringRef(myOptions->goalOutputFile), OutErrorInfo, llvm::sys::fs::F_None);

    if (OutErrorInfo == ok)
    {
      goalOutputFile_fs << std::to_string(GoalCounter::getInstance().counter);    
    }
    else
    {
      llvm::errs() << "Cannot open " << myOptions->goalOutputFile << " for writing\n";
    }

    goalOutputFile_fs.close();
  }
  
  if(GoalCounter::getInstance().mustGenerateFuncLabelMap)
  {
      std::cout << "GoalProFunc Dir: " << myOptions->goalProFuncOutputDir << std::endl;
      for(map<string,vector<string> >::const_iterator ptr=GoalCounter::getInstance().funcLabelMap->begin();
              ptr!=GoalCounter::getInstance().funcLabelMap->end();
              ptr++)
      {
          llvm::raw_fd_ostream goalProFunc_fs(llvm::StringRef(myOptions->goalProFuncOutputDir+"/"+ptr->first), OutErrorInfo, llvm::sys::fs::F_None);
          if (OutErrorInfo == ok)
          {
              
               for(vector<string>::const_iterator goal_name=ptr->second.begin();goal_name!=ptr->second.end(); goal_name++)
               {
                   goalProFunc_fs << *goal_name;
                   goalProFunc_fs<< "\n";                  
               }
                   
          }
          else
          {
              llvm::errs() << "Cannot open create file for function :  " << ptr->first << " \n";
          }
          goalProFunc_fs.close();      
          
      }
  }
  

  return 0;
}

