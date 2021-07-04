#include<TestVisitor.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Frontend/ASTUnit.h>

#include <clang/AST/ASTContext.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/AST/Stmt.h>
#include <clang/AST/StmtCXX.h>
#include <clang/AST/Expr.h>
#include <clang/AST/ExprCXX.h>
#include <clang/AST/Decl.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Rewrite/Frontend/Rewriters.h>
#include <clang/Basic/SourceManager.h>

#include <cstdio>
#include <memory>
#include <sstream>
#include <string>
#include <iostream>

#include <clang/AST/ASTConsumer.h>
#include <clang/Basic/FileManager.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Basic/TargetInfo.h>
#include <clang/Basic/TargetOptions.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Lex/Preprocessor.h>
#include <clang/Parse/ParseAST.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Rewrite/Frontend/Rewriters.h>
#include <llvm/Support/Host.h>
#include <llvm/Support/raw_ostream.h>
#include <clang/Lex/Token.h>
#include <clang/AST/ParentMap.h>


using namespace clang;
using namespace std;
#define l(line) std::cout << line << std::endl;

 
 tok::TokenKind getTokenKind(SourceLocation Loc, const SourceManager &SM, const ASTContext *Context) 
  {
      Token Tok;
      SourceLocation Beginning =Lexer::GetBeginningOfToken(Loc, SM, Context->getLangOpts());
      const bool Invalid =Lexer::getRawToken(Beginning, Tok, SM, Context->getLangOpts());
      //assert(!Invalid && "Expected a valid token.");
      if (Invalid)
          return tok::NUM_TOKENS;
      return Tok.getKind();
}
 StringRef GetText(Token &Tok, const SourceManager &Sources) 
 {
  return StringRef(Sources.getCharacterData(Tok.getLocation()),Tok.getLength());
}
  bool TestVisitor::VisitStmt(Stmt *s)
  {
    const SourceManager &sm = *TheHolder.SourceManager;
    const ASTContext & ctxt = *(TheHolder.ASTContext);
    const LangOptions & lo=TheRewriter.getLangOpts();
    l("--------------------BEGIN -----------"); 
    l(s->getLocStart().printToString(sm));
    s->dumpColor();
    l(s->getLocEnd().printToString(sm));
    l("--------------------END-----------"); 
    if(isa<IfStmt>(s))
    {
        IfStmt* ifs =cast<IfStmt>(s);
        Stmt * Then = ifs->getThen();
        Stmt *Else = ifs->getElse(); 
        if(!isa<CompoundStmt>(Then))
        {
            l("YYYYYYY");
            l(Then->getLocStart().getLocWithOffset(1).printToString(sm));
            TheRewriter.InsertTextAfter(Then->getLocStart().getLocWithOffset(1),"YYYYYYYYYYYYYYY");
            l("XXXXXXX");
            l(Then->getLocStart().getLocWithOffset(2).printToString(sm));
            TheRewriter.InsertTextAfter(Then->getLocStart().getLocWithOffset(2),"XXXXXXXXXX");
            if(Else)
            {
                int i= 0 ;
                SourceLocation intLoc= Else->getLocStart();
                while(i<20)
                {
                    i++;
                    tok::TokenKind  tk = getTokenKind(intLoc, sm,&ctxt);
                    if(tk  == tok::TokenKind::kw_else)
                    {
                        l("DONEEE");
                    }
                    llvm::outs() << "TOKEN=="<<  tok::getTokenName(tk) << "\r\n";
                    
                    intLoc = intLoc.getLocWithOffset(-1);
                    intLoc.dump(sm);
                    l("\n*********************************************");
                    
                }
                  
            }
                
        }
        
        if(Else)
        {
            SourceLocation nl = Lexer::findLocationAfterToken(Else->getLocEnd(),tok::semi,sm,lo,true);
            SourceLocation endd =Lexer::getLocForEndOfToken(Else->getLocEnd(), 0, sm, lo);
            
        }
        
    }
     
    return true;
  }
