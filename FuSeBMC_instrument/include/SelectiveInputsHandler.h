#ifndef SELECTIVEINPUTSHANDLER_H
#define SELECTIVEINPUTSHANDLER_H


#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Basic/SourceManager.h>
#include <clang/Frontend/ASTUnit.h>
#include <clang/AST/ASTContext.h>
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
#include <MyOptions.h>
using namespace clang;

class SelectiveInputsHandler
{
public:
	Stmt * mainBodyStmt = nullptr;
	std::vector<Stmt *> vctNonMainBodyStmt;
	ASTContext * aSTContext = nullptr;
	DeclRefExpr * nonDetDeclRefExpr = nullptr;
	Decl * nonDetDecl = nullptr;
	std::vector<BinaryOperator *> vctNotEqualBinaryOperators;
	std::vector<VarDecl *> vctVarDecls;
	std::vector<int64_t> vctSelectiveInputs;
	bool isCondValid = true;
	bool isIfFound = false;
	bool isSelectiveInputsFromMain = false;
	SelectiveInputsHandler(ASTContext * pASTContext);
	bool searchForSelectiveInputs();
	bool searchForSelectiveInputsInStmt(Stmt *s);
	string getFuncNameFromCallExpr(CallExpr * call);
	void handleCond(BinaryOperator * binaryOperator);
	bool isEqualNonDetDecl(Stmt * stmt, DeclRefExpr ** pDeclRefExpr);
	bool splitNotEqualOpInVarAndValue(BinaryOperator * p_NE_Operator,DeclRefExpr ** pDeclRefExpr,int64_t * pValue);
	void saveValueFromAndBinaryOperator(BinaryOperator * binaryOperator);
	BinaryOperator * getNotEqualBinaryOperatorFromExpr(Expr* expr);
	bool hasIfStmtOnlyReturn(IfStmt * ifStmt);
	bool isCompoundWithSingleReturn(Stmt * stmt);
	bool isReturnWithIntegerLiteral(Stmt * stmt);
	bool EvaluateAsInt(Stmt * stmt, int64_t * result);
	Stmt * removeParenExprFromStmt(Stmt * stmt);
	void reset();
	~SelectiveInputsHandler();
};


#endif /* SELECTIVEINPUTSHANDLER_H */

