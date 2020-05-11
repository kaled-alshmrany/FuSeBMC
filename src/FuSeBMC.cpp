#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
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

#include <FuSeBMC.h>
#include <MyVisitor.h>
#include <MyHolder.h>
#include <GoalCounter.h>
#include <iostream>
#include <fstream>


using namespace clang;

bool MustPrintGeneratedCode = false;

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


int main(int argc, char **argv)
{
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
  
  
  struct stat sb;
  if (argc < 5)
  {
     llvm::errs() << "Usage:" << argv[0] << " <inputFile> <outputFile> <goalOutputFile> <goalProFuncDir> <options>\n";
     llvm::errs() << "Usage:" << argv[0] << " <inputFile> <outputFile> <goalOutputFile> -nogoalProFunc <options>\n";
     return 1;
  }
  
   std::string inputFile(argv[1]);
   std::string outputFile(argv[2]);
   std::string goalOutputFile(argv[3]);
   std::string goalProFuncDir(argv[4]);
   if(goalProFuncDir != "-nogoalProFunc") 
       GoalCounter::getInstance().mustGenerateFuncLabelMap=true;
  //std::string fileName(argv[argc - 1]);
    
  // Make sure it exists
  if (stat(inputFile.c_str(), &sb) == -1)
  {
    perror(inputFile.c_str());
    exit(EXIT_FAILURE);
  }

  CompilerInstance compiler;
  DiagnosticOptions diagnosticOptions;
  compiler.createDiagnostics();
  //compiler.createDiagnostics(argc, argv);
  //Usage:" << ./my_instrument << " <inputFile> <outputFile> <goalOutputFile> <options>\n
  int new_args_count = argc - 4;
  char ** new_argv =(char**) malloc(sizeof(char *) * new_args_count);
  for(int i=0;i<new_args_count-1;i++)
  {
      new_argv[i] = argv[i+5];
  }
  
  new_argv[new_args_count-1] =argv[1] ; // inputFileName
  
  /*for(int i=0;i<new_args_count;i++)
  {
      std::cout << i << "=" << new_argv[i] << std::endl;
  }*/
  
  // Create an invocation that passes any flags to preprocessor
  CompilerInvocation *Invocation = new CompilerInvocation;
  bool compile_result = CompilerInvocation::CreateFromArgs(*Invocation, new_argv, new_argv + new_args_count - 1, compiler.getDiagnostics());
  if(!compile_result)
  {
      llvm::errs() << "Connot compile\n";
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

  const FileEntry *pFile = compiler.getFileManager().getFile(inputFile);
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

  // Convert <file>.c to <file_out>.c
  /*std::string outName (fileName);
  size_t ext = outName.rfind(".");
  if (ext == std::string::npos)
     ext = outName.length();
  outName.insert(ext, "_out");
   */
  
  std::error_code OutErrorInfo;
  std::error_code ok;
  llvm::raw_fd_ostream outFile(llvm::StringRef(outputFile), OutErrorInfo, llvm::sys::fs::F_None);
  

  if (OutErrorInfo == ok)
  {
    // Parse the AST
    clang::ParseAST(compiler.getPreprocessor(), &astConsumer, compiler.getASTContext());
    compiler.getDiagnosticClient().EndSourceFile();

    // Now output rewritten source code
    const RewriteBuffer *RewriteBuf = Rewrite.getRewriteBufferFor(compiler.getSourceManager().getMainFileID());
    std::cout << "Output to: " << outputFile << std::endl;
    outFile << std::string(RewriteBuf->begin(), RewriteBuf->end());
    if(MustPrintGeneratedCode)
        llvm::outs() << std::string(RewriteBuf->begin(), RewriteBuf->end());
  }
  else
  {
    llvm::errs() << "Cannot open " << outputFile << " for writing\n";
  }

  outFile.close();
  
  /***********/
  std::cout << "Output Goals to: " << goalOutputFile << std::endl;
  std::cout << "We have: " << GoalCounter::getInstance().counter << " Goals." << std::endl;
  llvm::raw_fd_ostream goalOutputFile_fs(llvm::StringRef(goalOutputFile), OutErrorInfo, llvm::sys::fs::F_None);

  if (OutErrorInfo == ok)
  {
    goalOutputFile_fs << std::to_string(GoalCounter::getInstance().counter);    
  }
  else
  {
    llvm::errs() << "Cannot open " << goalOutputFile << " for writing\n";
  }

  goalOutputFile_fs.close();
  if(GoalCounter::getInstance().mustGenerateFuncLabelMap)
  {
      std::cout << "GoalProFunc Dir: " << goalProFuncDir << std::endl;
      for(map<string,vector<string> >::const_iterator ptr=GoalCounter::getInstance().funcLabelMap->begin();
              ptr!=GoalCounter::getInstance().funcLabelMap->end();
              ptr++)
      {
          llvm::raw_fd_ostream goalProFunc_fs(llvm::StringRef(goalProFuncDir+"/"+ptr->first), OutErrorInfo, llvm::sys::fs::F_None);
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

