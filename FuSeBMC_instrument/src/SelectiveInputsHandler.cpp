#include <SelectiveInputsHandler.h>

SelectiveInputsHandler::SelectiveInputsHandler(ASTContext * pASTContext):
	aSTContext(pASTContext)
{
	//if(!pASTContext)
	//	std::cout << "context is NULL" << std::endl;
}
SelectiveInputsHandler::~SelectiveInputsHandler()
{
	
}
bool SelectiveInputsHandler::searchForSelectiveInputs()
{
	//this->mainBodyStmt->dumpColor();
	bool search_res = false;
	if(this->mainBodyStmt)
	{
		//std::cout << "starting selectiveInputs for main.." << std::endl;
		search_res = searchForSelectiveInputsInStmt(this->mainBodyStmt);
		if(this->vctSelectiveInputs.size() > 0)
		{
			this->isSelectiveInputsFromMain = true;
			return true;
		}
	}
	
	for(vector<Stmt *>::iterator it = this->vctNonMainBodyStmt.begin(); it != this->vctNonMainBodyStmt.end(); ++it)
	{
		this->reset();
		Stmt * nonMainBodyStmt = * it;
		//std::cout << "starting" << std::endl;
		//nonMainBodyStmt->dumpColor();
		search_res = searchForSelectiveInputsInStmt(nonMainBodyStmt);
		if(this->vctSelectiveInputs.size() > 0)
			return true;
	}
	
	return false;
}
bool SelectiveInputsHandler::searchForSelectiveInputsInStmt(Stmt *s)
{
	if(!s || s == nullptr) return false;
	if(isa<NullStmt>(s)) return false;
	for (Stmt::child_iterator i = s->child_begin(), e = s->child_end(); i != e; ++i)
	{
		Stmt * child = *i;
		if(!child) continue;
		if(isa<NullStmt>(child)) continue;
		if(isa<DeclStmt>(child))
		{
			DeclStmt * declStmt = cast<DeclStmt>(child);
			if(declStmt->isSingleDecl())
			{
				Decl * decl = declStmt->getSingleDecl();
				if(isa<VarDecl>(decl))
				{
					//std::cout << "We Have VAR DECL" << std::endl;
					VarDecl * varDecl = cast<VarDecl>(decl);
					this->vctVarDecls.push_back(varDecl);
					//varDecl->dumpColor();

					if(varDecl->hasInit())
					{
						//varDecl->getInit()->dumpColor();
						Stmt * expr = removeParenExprFromStmt(varDecl->getInit());
						if(isa<CallExpr>(expr))
						{
							CallExpr * callExpr = cast<CallExpr>(expr);
							string calleeName = getFuncNameFromCallExpr(callExpr);
							if (calleeName.rfind("__VERIFIER_nondet_", 0) == 0)
							{
								this->nonDetDecl = varDecl;
								//std::cout << "nonDetDecl" << std::endl;
							}
						}
					}
				}
			}
		}
		else
			if(isa<DeclRefExpr>(child))
			{
				DeclRefExpr * declRefExpr = cast<DeclRefExpr>(child);
				if(this->isIfFound == false &&  this->nonDetDecl != nullptr && this->nonDetDecl == declRefExpr->getDecl())
				{
					bool isVarReferenced = false;
					if(this->nonDetDeclRefExpr == nullptr)
						isVarReferenced = true;
					else 
						if(this->nonDetDeclRefExpr != nullptr && this->nonDetDeclRefExpr != declRefExpr)
							isVarReferenced = true;
					if(isVarReferenced)
					{
						//std::cout << "var is referenced" << std::endl;
						this->nonDetDecl = nullptr; // var is referenced before if stmt.
					}
				}
				//declRefExpr->dumpColor();
			}
			else
			if(isa<BinaryOperator>(child))
			{
				BinaryOperator * binaryOperator = cast<BinaryOperator>(child);
				if(binaryOperator->getOpcode() == BinaryOperatorKind::BO_Assign) // =
				{
					Stmt * lhs = removeParenExprFromStmt(binaryOperator->getLHS());
					Stmt * rhs = removeParenExprFromStmt(binaryOperator->getRHS());
					if(isa<DeclRefExpr>(lhs) && isa<CallExpr>(rhs))
					{
						CallExpr * call = cast<CallExpr>(rhs);
						string calleeName = getFuncNameFromCallExpr(call);
						if (calleeName.rfind("__VERIFIER_nondet_", 0) == 0) // string startswith prefix.
						{
							/*std::cout << "===== BEGIN =========" << std::endl;
							std::cout << "lhs=" << std::endl;
							lhs->dumpColor();
							std::cout << "rhs=" << std::endl;
							rhs->dumpColor();
							std::cout << "===== END =========" << std::endl;*/
						}
						DeclRefExpr * declRefExpr = cast<DeclRefExpr>(lhs);
						bool isDeclInMain = false;
						for(vector<VarDecl *>::iterator  it = this->vctVarDecls.begin(); it != this->vctVarDecls.end(); ++it)
						{
							if(declRefExpr->getDecl() == *it)
							{
								//std::cout << "IN MAIN" << std::endl;
								isDeclInMain = true;
								break;
							}
						}
						if(isDeclInMain)
						{
							this->nonDetDeclRefExpr = declRefExpr;
							this->nonDetDecl = declRefExpr->getDecl();
							string varName = declRefExpr->getNameInfo().getAsString();
							//std::cout << "varName=" << varName << std::endl;
						}
					}
				}
				//return true;
			}
			else
				if(isa<IfStmt>(child))
				{
					IfStmt * ifStmt = cast<IfStmt>(child);
					if(hasIfStmtOnlyReturn(ifStmt))
					{
						Stmt * cond = removeParenExprFromStmt(ifStmt->getCond());
						//cond->dumpColor();
						if(isa<BinaryOperator>(cond)) // binary cond
						{
							BinaryOperator * binaryOperator = cast<BinaryOperator>(cond);
							handleCond(binaryOperator);
							//if(binaryOperator->getOpcode() == BinaryOperatorKind::BO_LAnd) // boolean logical and
							//{
							//	saveValueFromAndBinaryOperator(binaryOperator);
							//}
							//std::cout << "isCondValid=" << isCondValid << std::endl;
							//std::cout << "vctNotEqualBinaryOperators=" << vctNotEqualBinaryOperators.size() << std::endl;
							if(isCondValid)
							{
								isIfFound = true;
								for(vector<BinaryOperator *>::iterator ptr = vctNotEqualBinaryOperators.begin(); 
										ptr != vctNotEqualBinaryOperators.end(); ptr++)
								{
									BinaryOperator * ne_op = * ptr;
									//std::cout << "NE Operator " << std::endl;
									//ne_op->dumpColor();
									DeclRefExpr * nonDetDeclRefExprFromNE = NULL;
									int64_t val = 0;
									if(splitNotEqualOpInVarAndValue(ne_op,&nonDetDeclRefExprFromNE,&val))
									{
										//std::cout << "The VALLL = " << val << std::endl;
										this->vctSelectiveInputs.push_back(val);
									}
									
									
									/*Stmt * nE_lh = removeParenExprFromStmt(ne_op->getLHS());
									Stmt * nE_rh = removeParenExprFromStmt(ne_op->getRHS());

									ImplicitCastExpr * implicitCastExpr = nullptr;
									Stmt * nonImplicitCastExpr = nullptr;
									if(isa<ImplicitCastExpr>(nE_lh))
									{
										implicitCastExpr = cast<ImplicitCastExpr>(nE_lh);
										nonImplicitCastExpr = nE_rh;
									}
									else if(isa<ImplicitCastExpr>(nE_rh))
									{
										implicitCastExpr = cast<ImplicitCastExpr>(nE_rh);
										nonImplicitCastExpr = nE_lh;
									}*/

									//if(isa<ImplicitCastExpr>(nE_lh) && isa<IntegerLiteral>(nE_rh))
									{
										//nE_lh->children()
										//std::cout << "YY_FOUND: IntegerLiteral" << std::endl;
										//ImplicitCastExpr * implicitCastExpr = cast<ImplicitCastExpr>(nE_lh);

									}
								}
								return true;
							} // if(isCondValid)
						}
					}
				} //if(isa<IfStmt>(child))
		
		searchForSelectiveInputsInStmt(child);
	}
	return false;
}
bool SelectiveInputsHandler::splitNotEqualOpInVarAndValue(BinaryOperator * p_NE_Operator,DeclRefExpr ** pDeclRefExpr,int64_t * pValue)
{
	Stmt * nE_lh = removeParenExprFromStmt(p_NE_Operator->getLHS());
	Stmt * nE_rh = removeParenExprFromStmt(p_NE_Operator->getRHS());
	if(isa<ImplicitCastExpr>(nE_lh) && isa<ImplicitCastExpr>(nE_rh)) //input != var1
	{
		//std::cout << "Both are ImplicitCastExpr" << std::endl;
		ImplicitCastExpr * implicitCastExpr_lh = cast<ImplicitCastExpr>(nE_lh);
		//ImplicitCastExpr * implicitCastExpr_rh = cast<ImplicitCastExpr>(nE_rh);
		DeclRefExpr * declRefExpr = NULL;
		if(isEqualNonDetDecl(implicitCastExpr_lh,&declRefExpr)) // input != var1
		{
			//std::cout << "ZZ_Count = 1" << std::endl;
			//std::cout << "FOUND DeclRefExpr : "<< __LINE__ << std::endl;
			//IntegerLiteral * integerLiteral = cast<IntegerLiteral>(nE_rh);
			//std::cout <<"VAL=" << integerLiteral->getValue().getLimitedValue()<< std::endl;
			int64_t val = 0;
			//nonImplicitCastExpr->dumpColor();
			if(this->EvaluateAsInt(nE_rh, &val))
			{
				*pValue = val;
				*pDeclRefExpr = declRefExpr;
				return true;
			}
		}
	}
	else
		if(isa<ImplicitCastExpr>(nE_lh) && !isa<ImplicitCastExpr>(nE_rh)) // input = 1
		{
			ImplicitCastExpr * implicitCastExpr_lh = cast<ImplicitCastExpr>(nE_lh);
			//ImplicitCastExpr * implicitCastExpr_rh = cast<ImplicitCastExpr>(nE_rh);
			DeclRefExpr * declRefExpr = NULL;
			if(isEqualNonDetDecl(implicitCastExpr_lh,&declRefExpr)) // input != var1
			{
				//std::cout << "ZZ_Count = 1" << std::endl;
				//std::cout << "FOUND DeclRefExpr" << std::endl;
				//IntegerLiteral * integerLiteral = cast<IntegerLiteral>(nE_rh);
				//std::cout <<"VAL=" << integerLiteral->getValue().getLimitedValue()<< std::endl;
				int64_t val = 0;
				//nonImplicitCastExpr->dumpColor();
				if(this->EvaluateAsInt(nE_rh, &val))
				{
					*pValue = val;
					*pDeclRefExpr = declRefExpr;
					return true;
				}
			}
			
		}
	return false;
}
bool SelectiveInputsHandler::isEqualNonDetDecl(Stmt * stmt, DeclRefExpr ** pDeclRefExpr)
{
	if(isa<ImplicitCastExpr>(stmt))
	{
		ImplicitCastExpr * implicitCastExpr = cast<ImplicitCastExpr>(stmt);
		int child_count = std::distance(implicitCastExpr->child_begin(), implicitCastExpr->child_end());
		if(child_count==1) // input != var1
		{
			//std::cout << "ZZ_Count = 1" << std::endl;
			Stmt * stmt_new = removeParenExprFromStmt(*(implicitCastExpr->child_begin()));
			if(isa<DeclRefExpr>(stmt_new))
			{
				//std::cout << "AA_DeclRefExpr" << std::endl;
				DeclRefExpr * declRefExpr = cast<DeclRefExpr>(stmt_new);
				if(this->nonDetDecl != nullptr && declRefExpr->getDecl() == this->nonDetDecl)
				{
					*pDeclRefExpr = declRefExpr;
					return true;
				}
			}
		}
	}
	return false;
}
void SelectiveInputsHandler::handleCond(BinaryOperator * binaryOperator)
{
	if(!isCondValid) return;
	if(binaryOperator->getOpcode() == BinaryOperatorKind::BO_NE)
	{
		vctNotEqualBinaryOperators.push_back(binaryOperator);
	}
	else
		if(binaryOperator->getOpcode() == BinaryOperatorKind::BO_LAnd)
		{
			Stmt * lhs = removeParenExprFromStmt(binaryOperator->getLHS());
			Stmt * rhs = removeParenExprFromStmt(binaryOperator->getRHS());
			
			if(isa<BinaryOperator>(lhs))
			{
				BinaryOperator * bo_lhs = cast<BinaryOperator>(lhs);
				handleCond(bo_lhs);
			}
			
			if(isa<BinaryOperator>(rhs))
			{
				BinaryOperator * bo_rhs = cast<BinaryOperator>(rhs);
				handleCond(bo_rhs);
			}
		}
		else
		{
			isCondValid = false;
			return;
		}
}
bool SelectiveInputsHandler::hasIfStmtOnlyReturn(IfStmt * ifStmt)
{
	Stmt * then = ifStmt->getThen();
	if(!then || then == nullptr)
		return false;
	if(isa<NullStmt>(then))
		return false;
	if(isReturnWithIntegerLiteral(then))
		return true;
	if(isCompoundWithSingleReturn(then))
		return true;
	return false;
}
bool SelectiveInputsHandler::isCompoundWithSingleReturn(Stmt * stmt)
{
	if(isa<CompoundStmt>(stmt))
	{
		for (Stmt::child_iterator i = stmt->child_begin(), e = stmt->child_end(); i != e; ++i)
		{
			Stmt * child = *i;
			if(isa<NullStmt>(child) || isa<LabelStmt>(child))
				continue;
			if(isReturnWithIntegerLiteral(child))
			{
				return true;
			}
			return false;
		}
	}
	return false;
}
bool SelectiveInputsHandler::EvaluateAsInt(Stmt * stmt, int64_t * result)
{
	if(!stmt || stmt == nullptr)
		return false;
	//std::cout << "EvaluateAsInt" << std::endl;
	//stmt->dumpColor();
	//return true;
	clang::Expr::EvalResult evalResult;
	if(isa<ImplicitCastExpr>(stmt))
	{
		//std::cout << "trying to Eval ImplicitCastExpr" << std::endl;
		ImplicitCastExpr * implicitCastExpr = cast<ImplicitCastExpr>(stmt);
		int child_count = std::distance(implicitCastExpr->child_begin(), implicitCastExpr->child_end());
		if(child_count==1)
		{
			Stmt * stmt_new = removeParenExprFromStmt(*(implicitCastExpr->child_begin()));
			if(isa<DeclRefExpr>(stmt_new))
			{
				DeclRefExpr * declRefExpr = cast<DeclRefExpr>(stmt_new);
				Decl * decl = declRefExpr->getDecl();
				//std::cout << "DDDDDDDDDDDDDDD" << std::endl;
				if(isa<VarDecl>(decl))
				{
					VarDecl * varDecl = cast<VarDecl>(decl);
					if(varDecl->hasInit())
					{
						Expr * exprInit= varDecl->getInit();
						bool canEvaluateAsInt = exprInit->EvaluateAsInt(evalResult, *(this->aSTContext));
						if(canEvaluateAsInt)
							if(evalResult.Val.isInt())
							{
								*result = evalResult.Val.getInt().getExtValue();
								return true;
							}
					}
				}
			}
		}
	}
	else
	if(isa<Expr>(stmt))
	{
		//std::cout << "IT IS EXPRE" << std::endl;
		Expr * expr = cast<Expr>(stmt);
		//return true;
		//if(this->aSTContext == nullptr)
		//	std::cout << "NULL PTR " << std::endl;
		//expr->dumpColor();
		bool canEvaluateAsInt = expr->EvaluateAsInt(evalResult, *(this->aSTContext));
		if(canEvaluateAsInt)
			if(evalResult.Val.isInt())
			{
				*result = evalResult.Val.getInt().getExtValue();
				return true;
			}
	}
	
	return false;
}
bool SelectiveInputsHandler::isReturnWithIntegerLiteral(Stmt * stmt)
{
	if(isa<ReturnStmt>(stmt))
	{
		ReturnStmt * returnStmt = cast<ReturnStmt>(stmt);
		Expr * retVal = returnStmt->getRetValue();
		if(!retVal || retVal == nullptr)
			return false;
		llvm::APSInt Val;
		clang::Expr::EvalResult evalResult;
		bool canEvaluateAsInt = retVal->EvaluateAsInt(evalResult, *this->aSTContext);
		//evalResult.hasSideEffects()
		if(isa<IntegerLiteral>(retVal) || canEvaluateAsInt)
			return true;
	}
	return false;
}
// Remove Parenthesis from Statment : ((((1)))) => 1
Stmt * SelectiveInputsHandler::removeParenExprFromStmt(Stmt * stmt)
{
	if(!stmt || stmt == nullptr)
		return stmt;
	if(isa<ParenExpr>(stmt))
	{
		ParenExpr * parenExpr = cast<ParenExpr>(stmt);
		int parenExprChildCount = std::distance(parenExpr->child_begin(), parenExpr->child_end());
		if(parenExprChildCount == 1)
		{
			//std::cout << "ZZ_Count = 1" << std::endl;
			Stmt * parenExprChild =*(parenExpr->child_begin());
			return removeParenExprFromStmt(parenExprChild);
		}
	}
	return stmt;
}

string SelectiveInputsHandler::getFuncNameFromCallExpr(CallExpr * call)
{
	if(!call || call == nullptr) return "";
	FunctionDecl * func_decl = call->getDirectCallee(); 
	if(func_decl)
	{
		IdentifierInfo * identifierInfo = func_decl->getIdentifier();
		if(identifierInfo)
		{
			llvm::StringRef funcName = identifierInfo->getName();
			string funcNameStr = funcName.str();
			return funcNameStr;
		}
	}
	return "";
}
void SelectiveInputsHandler::saveValueFromAndBinaryOperator(BinaryOperator * binaryOperator)
{
	Expr* op_lhs = binaryOperator->getLHS();
	if(isa<BinaryOperator>(op_lhs))
	{
		saveValueFromAndBinaryOperator(cast<BinaryOperator>(op_lhs));
	}
	//binaryOperator->EvaluateAsInt()
	Expr* op_rhs = binaryOperator->getRHS();
	//std::cout << "op_lhs=" << std::endl;
	//op_lhs->dumpColor();

	//std::cout << "op_rhs=" << std::endl;
	//op_rhs->dumpColor();
	BinaryOperator * rhs_NE_op = getNotEqualBinaryOperatorFromExpr(op_rhs);
	if(rhs_NE_op != nullptr)
	{
		//std::cout << "XX_FOUND: rhs_NE_op" << std::endl;
		Expr * nE_lh = rhs_NE_op->getLHS();
		Expr * nE_rh = rhs_NE_op->getRHS();
		if(isa<ImplicitCastExpr>(nE_lh) && isa<IntegerLiteral>(nE_rh))
		{
			//nE_lh->children()
			//std::cout << "YY_FOUND: IntegerLiteral" << std::endl;
			ImplicitCastExpr * implicitCastExpr = cast<ImplicitCastExpr>(nE_lh);
			int implicitCastExprChildCount = std::distance(implicitCastExpr->child_begin(), implicitCastExpr->child_end());
			if(implicitCastExprChildCount==1)
			{
				//std::cout << "ZZ_Count = 1" << std::endl;
				Stmt * implicitCastExprChild =*(implicitCastExpr->child_begin());
				if(isa<DeclRefExpr>(implicitCastExprChild))
				{
					//std::cout << "AA_DeclRefExpr" << std::endl;
					DeclRefExpr * declRefExpr = cast<DeclRefExpr>(implicitCastExprChild);
					
					if(this->nonDetDecl != nullptr)
						if(declRefExpr->getDecl() == nonDetDecl)
						{
							//std::cout << "BB_FOUND" << std::endl;
							IntegerLiteral * integerLiteral = cast<IntegerLiteral>(nE_rh);
							//std::cout <<"VAL=" << integerLiteral->getValue().getLimitedValue()<< std::endl;
						}
				}
			}
		}
	}
}
BinaryOperator * SelectiveInputsHandler::getNotEqualBinaryOperatorFromExpr(Expr* expr)
{
	if(isa<BinaryOperator>(expr))
	{
		BinaryOperator * binaryOperator = cast<BinaryOperator>(expr);
		if(binaryOperator->getOpcode() == BinaryOperatorKind::BO_NE)
			return binaryOperator;
	}
	else
	{
		for (Stmt::child_iterator i = expr->child_begin(), e = expr->child_end(); i != e; ++i)
		{
			Stmt * child = *i;
			if(isa<Expr>(child))
			{
				Expr* child_as_exp = cast<Expr>(child);
				BinaryOperator * someBo = this->getNotEqualBinaryOperatorFromExpr(child_as_exp);
				if(someBo != nullptr)
					return someBo;
			}
		}
	}
	return nullptr;
}
void SelectiveInputsHandler::reset()
{
	nonDetDeclRefExpr = nullptr;
	nonDetDecl = nullptr;
	vctNotEqualBinaryOperators.clear();
	vctVarDecls.clear();
	vctSelectiveInputs.clear();
	isCondValid = true;
	isIfFound = false;
	isSelectiveInputsFromMain = false;
}