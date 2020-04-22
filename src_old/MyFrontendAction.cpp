#include <MyFrontendAction.h>

std::unique_ptr<clang::ASTConsumer> MyFrontendAction::CreateASTConsumer(clang::CompilerInstance &Compiler, llvm::StringRef InFile)
{
    return std::unique_ptr<clang::ASTConsumer>(new ASTConsumer());
}

