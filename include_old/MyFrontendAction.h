#ifndef MYFRONTENDACTION_H
#define MYFRONTENDACTION_H

#include <clang/Frontend/FrontendActions.h>
#include <MyASTConsumer.h>


class MyFrontendAction : public clang::ASTFrontendAction
{
public:
  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(clang::CompilerInstance &Compiler, llvm::StringRef InFile);
  
};


#endif 

