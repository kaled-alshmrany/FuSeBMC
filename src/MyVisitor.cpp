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

#include <cstdio>
#include <memory>
#include <sstream>
#include <string>
#include <iostream>

#include <MyHolder.h>
#include <MyVisitor.h>
#include <GoalCounter.h>
#include <MyOptions.h>
#include <my_instrument.h>
//#include <clang/ASTMatchers/ASTMatchFinder.h>
//#include <clang/ASTMatchers/ASTMatchers.h>

using namespace clang;
extern MyOptions * myOptions;
#ifdef MYDEBUG
    int V_counter =0 ;
    #define GET_LINE() "\n/*B_"+std::to_string(__LINE__)+"_("+ std::to_string(++V_counter) +")"+"*/\n"
    #define GET_LINE_E() "\n/*E_"+std::to_string(__LINE__)+"_("+ std::to_string(V_counter) +")"+"*/\n"
#else
    #define GET_LINE() std::string("")
    #define GET_LINE_E() std::string("")
#endif

bool MyVisitor::TraverseDecl(Decl* decl)
  {
      //llvm::outs() << "TTTTTTTT";
      //decl->dumpColor();
      //if(decl->isFunctionOrFunctionTemplate()) 
      //{
       //   FunctionDecl *func = decl->getAsFunction();
          //const SourceManager &SM = *TheHolder.SourceManager;
          //const ASTContext *Context = TheHolder.ASTContext;
          
          //16.05.2020
          //if(func->hasBody())
          //{
           //   Stmt * body =func->getBody();
            //  for (Stmt::child_iterator i = body->child_begin(), e = body->child_end(); i != e; ++i)
             // {
             //     Stmt *currStmt = *i;
              //    if(isa<ReturnStmt>(currStmt))
               //   {
                //      ReturnStmt * retStmt =cast<ReturnStmt>(currStmt);
                      //std::cout << "BEGIN STMMT" << std::endl;
                      //retStmt->dumpColor();
                      //std::cout << "END STMMT" << std::endl;
                //      TheRewriter.InsertTextBefore(retStmt->getLocStart().getLocWithOffset(0) ,"/*my return goal*/"+GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString())+"");
                //  }
              //}
              //TheRewriter.InsertTextAfter(body->getLocStart().getLocWithOffset(1),"\r\n" + GoalCounter::getInstance().GetNewGoalForFunc(func->getNameAsString()));
        //  }
      //}
      //return true;
      return Base::TraverseDecl(decl);
  }
  tok::TokenKind MyVisitor::getTokenKind(SourceLocation Loc, const SourceManager &SM, const ASTContext *Context) 
  {
      Token Tok;
      SourceLocation Beginning =Lexer::GetBeginningOfToken(Loc, SM, Context->getLangOpts());
      const bool Invalid =Lexer::getRawToken(Beginning, Tok, SM, Context->getLangOpts());
      //assert(!Invalid && "Expected a valid token.");
      if (Invalid)
          return tok::NUM_TOKENS;
      return Tok.getKind();
}
  /*static SmallVector<const Stmt *, 1> getParentStmts(const Stmt *S,ASTContext *Context) {
  SmallVector<const Stmt *, 1> Result;
  ASTContext::DynTypedNodeList Parents = Context->getParents(*S);
  SmallVector<ast_type_traits::DynTypedNode, 1> NodesToProcess(Parents.begin(),Parents.end());
  while (!NodesToProcess.empty())
  {
    ast_type_traits::DynTypedNode Node = NodesToProcess.back();
    NodesToProcess.pop_back();

    if (const auto *S = Node.get<Stmt>()) {
      Result.push_back(S);
    } else {
      Parents = Context->getParents(Node);
      NodesToProcess.append(Parents.begin(), Parents.end());
    }
  }
  return Result;
}
  */
  
  bool MyVisitor::checkStmt(Stmt *S,SourceLocation InitialLoc, SourceLocation EndLocHint, InstrumentOption instrumentOption) 
  {
  // 1) If there's a corresponding "else" or "while", the check inserts "} "
  // right before that token.
  // 2) If there's a multi-line block comment starting on the same line after
  // the location we're inserting the closing brace at, or there's a non-comment
  // token, the check inserts "\n}" right before that token.
  // 3) Otherwise the check finds the end of line (possibly after some block or
  // line comments) and inserts "\n}" right before that EOL.
  if (!S) return false;  
  //llvm::outs()<< "SSSSSSSSSSSSSS\r\n" << S->getStmtClassName() ;
  //S->dumpColor();
    
  const SourceManager &SM = *TheHolder.SourceManager;
  ASTContext *Context = TheHolder.ASTContext;
  
   // Already inside braces.
  if(isa<CompoundStmt>(S))
  {
      //while(x){compound_statment} ; if(x){compund_sttement}
      CompoundStmt * compoundStmt = cast<CompoundStmt>(S);
      if(myOptions->addLabels)
          TheRewriter.InsertTextAfter(compoundStmt->getLBracLoc().getLocWithOffset(1),
              (hasOneCompoundChild(compoundStmt)? "" : GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString()))
      );
      //16.05.2020
      if(instrumentOption == InstrumentOption::MUST_INSERT_ELSE && myOptions->addElse)
          TheRewriter.InsertTextBefore(compoundStmt->getRBracLoc().getLocWithOffset(1),GET_LINE()+"\nelse\n {"+GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString())+"}"+GET_LINE_E());       
           
      return false;
      /*bool isDone=false;
      SourceLocation LParenLoc =forwardSkipWhitespaceAndComments(S->getLocStart(), SM, Context);
      while(!isDone)
      {        
        if (LParenLoc.isInvalid())
        {
            return true;
        }
        tok::TokenKind TokKind = getTokenKind(LParenLoc,SM,Context);
        llvm::outs() << "TOKEN=="<<  tok::getTokenName(TokKind) << "\r\n";
        if (TokKind == tok::l_brace)
        {
            //diag(RParenLoc, ErrorMessage);
            TheRewriter.InsertTextAfter(LParenLoc.getLocWithOffset(1),GoalCounter::getInstance().GetNewGoal());
            isDone=true;
        }
        else
        {
            LParenLoc=LParenLoc.getLocWithOffset(1);
            llvm::outs() << "XXX=="<<  LParenLoc.printToString(SM) << "\r\n";
            //RParenLoc =forwardSkipWhitespaceAndComments(RParenLoc, SM, Context);
        }
      }*/
      
       /*InitialLoc = Lexer::makeFileCharRange(
                   CharSourceRange::getCharRange(InitialLoc, S->getLocStart()),
                   SM, Context->getLangOpts()).getBegin();
       if (InitialLoc.isInvalid())
           return false;
       SourceLocation StartLoc =Lexer::getLocForEndOfToken(InitialLoc, 0, SM, Context->getLangOpts());
      TheRewriter.InsertTextAfter(StartLoc,"GOAL_AAAA:");*/
  }
  
  // Treat macros.
  CharSourceRange FileRange = Lexer::makeFileCharRange(CharSourceRange::getTokenRange(S->getSourceRange()), SM,Context->getLangOpts());
  if (FileRange.isInvalid())
    return false;

  // InitialLoc points at the last token before opening brace to be inserted.
  assert(InitialLoc.isValid());
  // Convert InitialLoc to file location, if it's on the same macro expansion
  // level as the start of the statement. We also need file locations for
  // Lexer::getLocForEndOfToken working properly.
  InitialLoc = Lexer::makeFileCharRange(
                   CharSourceRange::getCharRange(InitialLoc, S->getLocStart()),
                   SM, Context->getLangOpts()).getBegin();
  if (InitialLoc.isInvalid())
    return false;
  SourceLocation StartLoc =Lexer::getLocForEndOfToken(InitialLoc, 0, SM, Context->getLangOpts());

  // StartLoc points at the location of the opening brace to be inserted.
  SourceLocation EndLoc;
  std::string ClosingInsertion;
  if (EndLocHint.isValid())
  {
      EndLoc = EndLocHint;
      ClosingInsertion = "\n/*A*/}\n";
      //TheRewriter.InsertTextAfter(EndLoc,ClosingInsertion);
  } 
  else 
  {
      const auto FREnd = FileRange.getEnd().getLocWithOffset(-1);
      EndLoc = findEndLocation(FREnd, SM, Context);
      ClosingInsertion = "\n/*B*/}\n";
      //TheRewriter.InsertTextAfter(EndLoc,ClosingInsertion);
  }
  assert(StartLoc.isValid());
  assert(EndLoc.isValid());
  // Don't require braces for statements spanning less than certain number of lines.
  //unsigned StartLine = SM.getSpellingLineNumber(StartLoc);
  //auto Diag = diag(StartLoc,"statement should be inside braces");
  //Diag << FixItHint::CreateInsertion(StartLoc, " {")
  //     << FixItHint::CreateInsertion(EndLoc, ClosingInsertion);
  if(myOptions->addLabels) TheRewriter.InsertTextAfter(StartLoc,GET_LINE()+"\n{\n" +
  ((hasOneCompoundChild(S)?"" : GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString())))
  
  + GET_LINE_E());
  if(instrumentOption == InstrumentOption::MUST_INSERT_ELSE && myOptions->addElse)
  {
      TheRewriter.InsertTextBefore(EndLoc,GET_LINE()+ClosingInsertion+"else \n{"+GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString())+"}"+GET_LINE_E());
  }
  else 
  {
#ifdef MYDEBUG
      //std::cout << "LINE:"<< EndLoc.printToString(SM) << " V_counter:" << V_counter << std::endl;
#endif
      if(myOptions->addLabels) TheRewriter.InsertTextBefore(EndLoc,GET_LINE()+ClosingInsertion+GET_LINE_E());
  }
  return true;
}
 void MyVisitor::check(Stmt * S)
 {
     const SourceManager &SM = *(TheHolder.SourceManager);
     const ASTContext *Context = TheHolder.ASTContext;

    // Get location of closing parenthesis or 'do' to insert opening brace.
    if (isa<ForStmt>(S))
    {
        ForStmt *forStmt = cast<ForStmt>(S);
        checkStmt(forStmt->getBody(),forStmt->getRParenLoc());
    }
    else if (isa<CXXForRangeStmt>(S))
    {
        CXXForRangeStmt * cXXForRangeStmt=cast<CXXForRangeStmt>(S);
        checkStmt(cXXForRangeStmt->getBody(), cXXForRangeStmt->getRParenLoc());
    }
    else if (isa<DoStmt>(S))
    {
        DoStmt * doStmt=cast<DoStmt>(S);
        checkStmt(doStmt->getBody(), doStmt->getDoLoc(), doStmt->getWhileLoc());
    } 
    else if (isa<WhileStmt>(S))
    {
        WhileStmt * whileStmt=cast<WhileStmt>(S);
        SourceLocation StartLoc = findRParenLoc(whileStmt, SM, Context);
        if (StartLoc.isInvalid())
            return;
      checkStmt(whileStmt->getBody(), StartLoc);
    } 
    else if(isa<IfStmt>(S))
    {
        IfStmt * ifStmt = cast<IfStmt>(S);
        SourceLocation StartLoc = findRParenLoc(ifStmt, SM, Context);
        if (StartLoc.isInvalid())
            return;
        //if (ForceBracesStmts.erase(S))
        //    ForceBracesStmts.insert(ifStmt->getThen());
        
        Stmt *Else = ifStmt->getElse();
        
        //if(Else && !isa<IfStmt>(Else))
        if (Else) 
        {
            // Omit 'else if' statements here, they will be handled directly.
            checkStmt(ifStmt->getThen(), StartLoc, ifStmt->getElseLoc(),InstrumentOption::STMT_OPTION_NONE );
            checkStmt(Else, ifStmt->getElseLoc(), SourceLocation());
        }
        else
        {
            // Strart: 16.05.2020
            //ifStmt->getThen()->getLocEnd()
            //std::cout << SM.getCharacterData(ifStmt->getThen()->getLocEnd()) << std::endl;
            //TheRewriter.InsertTextAfter(ifStmt->getThen()->getLocEnd().getLocWithOffset(1),"else {houssam"+GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString())+"}");
            checkStmt(ifStmt->getThen(), StartLoc, ifStmt->getElseLoc(),InstrumentOption::MUST_INSERT_ELSE);
            
        }
    }
    /*else if(isa<CompoundStmt>(S))
    {
        CompoundStmt * compoundStmt = cast<CompoundStmt>(S);
        TheRewriter.InsertTextAfter(compoundStmt->getRBracLoc().getLocWithOffset(-1),"\n;GOAL_XX:;\n");

    }*/
    /*else if(isa<DeclStmt>(S))
    {
        llvm::outs()<< "\nSSSSSSSSSSSSSS\r\n" << S->getStmtClassName() ;
        S->dumpColor();
    }*/
    else if(isa<SwitchStmt>(S))
    {
        //llvm::outs()<<  current_func->getNameAsString() << "\n";
         SwitchStmt * switchStmt = cast<SwitchStmt>(S);
         const SwitchCase * switchCase = switchStmt->getSwitchCaseList();
         while(switchCase != nullptr)
         {
            if(myOptions->addLabels) TheRewriter.InsertTextAfter(switchCase->getColonLoc().getLocWithOffset(1),GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString()));
            switchCase = switchCase->getNextSwitchCase();
         }
         
        //llvm::outs()<< "\nXXXXXXXXXX\r\n" << S->getStmtClassName() ;
        //S->dumpColor();
    }
    else
    {
      //llvm_unreachable("Invalid match");
       //llvm::outs()<< "\nSSSSSSSSSSSSSS\r\n" << S->getStmtClassName() ;
        //llvm::outs()<< S->getLocStart().printToString(SM) << "\n";
        //S->dumpColor();

    }
}
 template <typename IfOrWhileStmt>
SourceLocation MyVisitor::findRParenLoc(const IfOrWhileStmt *S,const SourceManager &SM,const ASTContext *Context)
 {
  // Skip macros.
  if (S->getLocStart().isMacroID())
    return SourceLocation();

//  static const char *const ErrorMessage ="cannot find location of closing parenthesis ')'";
  SourceLocation CondEndLoc = S->getCond()->getLocEnd();
  if (const DeclStmt *CondVar = S->getConditionVariableDeclStmt())
    CondEndLoc = CondVar->getLocEnd();

  assert(CondEndLoc.isValid());
  /*if(!CondEndLoc.isValid())
  {
      S->dump();
      const SourceManager &SM = *TheHolder.SourceManager;
      const ASTContext *Context = TheHolder.ASTContext;
      S->getLocStart().dump(SM);
      exit(0);
  }*/
  SourceLocation PastCondEndLoc = Lexer::getLocForEndOfToken(CondEndLoc, 0, SM, Context->getLangOpts());
  if (PastCondEndLoc.isInvalid()) 
  {
    //diag(CondEndLoc, ErrorMessage);
    return SourceLocation();
  }
  SourceLocation RParenLoc =forwardSkipWhitespaceAndComments(PastCondEndLoc, SM, Context);
  if (RParenLoc.isInvalid())
  {
    //diag(PastCondEndLoc, ErrorMessage);
    return SourceLocation();
  }
  tok::TokenKind TokKind = getTokenKind(RParenLoc, SM, Context);
  if (TokKind != tok::r_paren)
  {
    //diag(RParenLoc, ErrorMessage);
    return SourceLocation();
  }
  return RParenLoc;
}
 
 SourceLocation MyVisitor::forwardSkipWhitespaceAndComments(SourceLocation Loc,const SourceManager &SM,const ASTContext *Context) 
 {
     assert(Loc.isValid());
     for (;;) 
     {
         while (isWhitespace(*FullSourceLoc(Loc, SM).getCharacterData()))
             Loc = Loc.getLocWithOffset(1);
         tok::TokenKind TokKind = getTokenKind(Loc, SM, Context);
         if (TokKind == tok::NUM_TOKENS || TokKind != tok::comment)
             return Loc;
         // Fast-forward current token.
         Loc = Lexer::getLocForEndOfToken(Loc, 0, SM, Context->getLangOpts());
     }
}
 
SourceLocation MyVisitor::findEndLocation(SourceLocation LastTokenLoc,const SourceManager &SM,const ASTContext *Context) 
{
    SourceLocation Loc = LastTokenLoc;
    // Loc points to the beginning of the last (non-comment non-ws) token
    // before end or ';'.
    assert(Loc.isValid());
    bool SkipEndWhitespaceAndComments = true;
    tok::TokenKind TokKind = getTokenKind(Loc, SM, Context);
    if (TokKind == tok::NUM_TOKENS || TokKind == tok::semi || TokKind == tok::r_brace) 
    {
        // If we are at ";" or "}", we found the last token. We could use as well
        // `if (isa<NullStmt>(S))`, but it wouldn't work for nested statements.
        SkipEndWhitespaceAndComments = false;
    }
    Loc = Lexer::getLocForEndOfToken(Loc, 0, SM, Context->getLangOpts());
    // Loc points past the last token before end or after ';'.
    if (SkipEndWhitespaceAndComments)
    {
        Loc = forwardSkipWhitespaceAndComments(Loc, SM, Context);
        tok::TokenKind TokKind = getTokenKind(Loc, SM, Context);
        if (TokKind == tok::semi)
            Loc = Lexer::getLocForEndOfToken(Loc, 0, SM, Context->getLangOpts());
    }
    for (;;)
    {
        assert(Loc.isValid());
        while (isHorizontalWhitespace(*FullSourceLoc(Loc, SM).getCharacterData()))
            Loc = Loc.getLocWithOffset(1);
        if (isVerticalWhitespace(*FullSourceLoc(Loc, SM).getCharacterData())) 
        {
            // EOL, insert brace before.
            break;
        }
        tok::TokenKind TokKind = getTokenKind(Loc, SM, Context);
        if (TokKind != tok::comment)
        {
            // Non-comment token, insert brace before.
            break;
        }
        SourceLocation TokEndLoc =Lexer::getLocForEndOfToken(Loc, 0, SM, Context->getLangOpts());
        SourceRange TokRange(Loc, TokEndLoc);
        StringRef Comment = Lexer::getSourceText(CharSourceRange::getTokenRange(TokRange), SM, Context->getLangOpts());
        if (Comment.startswith("/*") && Comment.find('\n') != StringRef::npos) 
        {
            // Multi-line block comment, insert brace before.
            break;
        }
        // else: Trailing comment, insert brace after the newline.
        // Fast-forward current token.
        Loc = TokEndLoc;
    }
    return Loc;
}

bool MyVisitor::VisitDecl(Decl *decl)
{
    if (decl->isFunctionOrFunctionTemplate())
        this->current_func = decl->getAsFunction();
   
     //16.05.2020
     if(decl->isFunctionOrFunctionTemplate() && decl->hasBody() && myOptions->addGoalAtEndOfFunc)         
     {
         Stmt*  body =decl->getBody();
         // Iterate over the top level of statements; 
         //not insert before
         // I don't know if we must check if the sub-statements include 'return'
         bool hasReturn = false;
         for (Stmt::child_iterator i = body->child_begin(), e = body->child_end(); i != e; ++i)
         {
             Stmt *currStmt = *i;
             if(isa<ReturnStmt>(currStmt))
             {
                 hasReturn=true;
                 ReturnStmt * retStmt =cast<ReturnStmt>(currStmt);
                  //std::cout << "BEGIN STMMT" << std::endl;
                  //retStmt->dumpColor();
                  //std::cout << "END STMMT" << std::endl;
                 TheRewriter.InsertTextBefore(retStmt->getLocStart().getLocWithOffset(0) ,GET_LINE()+GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString())+"");
             }
            
         }
         // NOTE : insert Before
         if(!hasReturn)
             TheRewriter.InsertTextBefore(body->getLocEnd().getLocWithOffset(0),GET_LINE() + GoalCounter::getInstance().GetNewGoalForFunc(current_func->getNameAsString()));
         
     }
      //20.05.2020
    if(decl->isFunctionOrFunctionTemplate() && decl->hasBody())
    {
        std::string lbl =myOptions->GetLabelForFunc(this->current_func->getNameAsString());
        if(!lbl.empty())
        {
            Stmt*  body =decl->getBody();
            bool hasLbl = isLabelExistsInStement(body,lbl);            
            if(!hasLbl)TheRewriter.InsertTextBefore(body->getLocStart().getLocWithOffset(1),GET_LINE()+lbl+":;\n");            
        }
    }
     return true;
  }

/** Defined in super class, will be automatically called*/

  bool MyVisitor::VisitStmt(Stmt *s)
  {
      if(!s) return true;
      //llvm::outs() << "SSSSSSSSSSSSSSSs\r\n" ;
      //const SourceManager &SM = *TheHolder.SourceManager;
      //const ASTContext *Context = TheHolder.ASTContext;
     
      if(myOptions->showParseTree)
      {
          s->dumpColor();
          //s->getLocStart().dump(SM);
      }
      check(s);
      //llvm::outs() << "---------------------------------------\r\n" ;
    // Only care about If statements.
    //if (isa<IfStmt>(s))
    {
       
        /*IfStmt *IfStatement = cast<IfStmt>(s);
        Stmt *Then = IfStatement->getThen();
        SourceLocation loc=Then->getLocStart();
        while (isWhitespace(*FullSourceLoc(loc,TheRewriter.getSourceMgr()).getCharacterData()))
            loc = loc.getLocWithOffset(1);
        tok::TokenKind TokKind = getTokenKind(loc,TheRewriter.getSourceMgr(),&TheHolder.ASTContext);
        if(TokKind==tok::TokenKind::l_brace)
            TheRewriter.InsertText(loc.getLocWithOffset(1), "GOAL_1:\n", true,true);
        Stmt *Else = IfStatement->getElse();
        if (Else)
        {
            SourceLocation loc=Else->getLocStart();
            while (isWhitespace(*FullSourceLoc(loc,TheRewriter.getSourceMgr()).getCharacterData()))
                loc = loc.getLocWithOffset(1);
            TheRewriter.InsertText(loc.getLocWithOffset(1), "GOAL_2:\n", true,true);
        }  */      
    }
      return true;
  }  
bool isLabelExistsInStement(Stmt * s , std::string & lbl)
{
    if(isa<LabelStmt>(s))
    {
        LabelStmt * lblStmt =cast<LabelStmt>(s);
        if(lbl==lblStmt->getName())
            return true;
    }
    for (Stmt::child_iterator i = s->child_begin(), e = s->child_end(); i != e; ++i)
    {
        Stmt *currStmt = *i;
        if(isLabelExistsInStement(currStmt,lbl))
            return true;
    }
    return false;
  }
bool hasOneCompoundChild(Stmt * s)
{
    /*unsigned int count =0;
    for (Stmt::child_iterator i = s->child_begin(), e = s->child_end(); i != e; ++i)
    {
        count++;
    }
    if(count==1)
    {
        Stmt * child= *(s->child_begin());
         if(isa<IfStmt>(child) || isa<ForStmt>(child) || isa<WhileStmt>(child) || isa<CXXForRangeStmt>(child)
                 || isa<SwitchStmt>(child) || isa<DoStmt>(child))
             return true;
        
    }
    return false;
*/
    return false;
}
