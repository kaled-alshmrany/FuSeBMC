#ifndef MYASTCONSUMER_H
#define MYASTCONSUMER_H

#include <MyVisitor.h>
#include <MyHolder.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Rewrite/Frontend/Rewriters.h>

class MyASTConsumer : public clang::ASTConsumer
{
    private:
        MyVisitor Visitor;
        //MyHolder  TheHolder;
public:
  MyASTConsumer(clang::Rewriter &R,MyHolder& H):Visitor(R,H) 
  {
  }
  virtual void HandleTranslationUnit(clang::ASTContext &Context) 
  {

    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }
};

#endif 

