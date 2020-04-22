#include <clang/Tooling/Tooling.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Frontend/ASTUnit.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Parse/ParseAST.h>
#include <clang/Basic/SourceManager.h>
#include <MyFrontendAction.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Rewrite/Frontend/Rewriters.h>

#include <clang/Basic/Diagnostic.h>
#include <clang/Lex/HeaderSearchOptions.h>
#include <clang/Lex/HeaderSearch.h>
#include <clang/Driver/Driver.h>
#include <llvm/Option/OptTable.h>
#include <clang/Driver/Options.h>
#include <clang/Driver/Compilation.h>


#include <MyHolder.h>
#include <MyVisitor.h>
#include <bits/shared_ptr.h>



//using namespace llvm;
using namespace clang;
using namespace clang::tooling;

static llvm::cl::OptionCategory MyToolCategory("my-tool options");
//static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

void mydebug(char * str)
{
    llvm::errs()<< str ;
    llvm::errs()<< "\r\n" ;
    llvm::errs()<< "-----------------------" ;
    llvm::errs()<< "\r\n" ;
}
int main(int argc, const char** argv)
{
    
    CompilerInstance TheCompInst;
    TheCompInst.createDiagnostics();
    
    LangOptions &lo = TheCompInst.getLangOpts();
    lo.CPlusPlus = 1;
    lo.CPlusPlus11 = 1;
    //lo.CPlusPlus14 = 1;
    //lo.C99 = 1;
    
    
  lo.Bool = true;
  lo.WChar = true;
  lo.Blocks = true;
  lo.DebuggerSupport = true;
  lo.SpellChecking = false;
  lo.ThreadsafeStatics = false;
  lo.AccessControl = false;
  lo.DollarIdents = true;
  lo.Exceptions = true;
  lo.CXXExceptions = true;
  lo.NoBuiltin=false;
  lo.GNUMode = true;
 
    
    // Initialize target info with the default triple for our platform.
    std::shared_ptr<clang::TargetOptions> TO = std::make_shared<clang::TargetOptions>();
    //TO->Triple = llvm::sys::getDefaultTargetTriple();
    TO->Triple = "x86_64-unknown-linux-gnu";
    TO->CPU = "x86-64";

    TargetInfo *TI = TargetInfo::CreateTargetInfo(TheCompInst.getDiagnostics(),TO);
    TheCompInst.setTarget(TI);
    TheCompInst.getTargetOpts() = *TO;
    clang::FileManager *  fileManager = new clang::FileManager(clang::FileSystemOptions());
    TheCompInst.setFileManager(fileManager);
    //TheCompInst.createFileManager();
    FileManager &FileMgr = TheCompInst.getFileManager();

    TheCompInst.createSourceManager(FileMgr);
    
    SourceManager &SourceMgr = TheCompInst.getSourceManager();
    
    
    // A Rewriter helps us manage the code rewriting task.
    Rewriter TheRewriter;
    TheRewriter.setSourceMgr(SourceMgr,lo);
    HeaderSearchOptions& headerSearchOptions=TheCompInst.getHeaderSearchOpts();
    //headerSearchOptions.AddPath(std::string("/usr/include"),clang::frontend::IncludeDirGroup::Angled, false, false);
    
    //headerSearchOptions.AddPath(std::string("/usr/lib/gcc/x86_64-linux-gnu/9/include"), clang::frontend::Angled, false, false);
    headerSearchOptions.AddPath(std::string("/home/kaled/clang_base/lib/clang/6.0.0/include"), clang::frontend::Angled, false, false);
    headerSearchOptions.AddPath(std::string("/usr/include"),clang::frontend::Angled, false, false);
    headerSearchOptions.AddPath(std::string("/usr/include/linux"), clang::frontend::Angled, false, false);
    headerSearchOptions.AddPath(std::string("/usr/include/c++/9/tr1"), clang::frontend::Angled, false, false);
    headerSearchOptions.AddPath(std::string("/usr/include/c++/9"), clang::frontend::Angled, false, false);
    headerSearchOptions.AddPath(std::string("/home/kaled/sdb1/uFTP/library"), clang::frontend::Angled, false, false);
    
    
    
    headerSearchOptions.UseBuiltinIncludes = true;
    headerSearchOptions.UseStandardSystemIncludes = true;
    headerSearchOptions.UseStandardCXXIncludes = true;
    headerSearchOptions.UseLibcxx=true;
    headerSearchOptions.UseDebugInfo=true;
    headerSearchOptions.Verbose=true;
    
    clang::HeaderSearch headerSearch(std::shared_ptr<HeaderSearchOptions>(&headerSearchOptions),SourceMgr, TheCompInst.getDiagnostics(),lo, TI);    
    //headerSearch.AddSearchPath(clang::DirectoryLookup(FileMgr.getDirectory("/usr/include"),clang::SrcMgr::C_System, false), true);

    clang::ApplyHeaderSearchOptions(headerSearch, headerSearchOptions,lo,TI->getTriple());
    
    clang::CompilerInvocation &compInvocation = TheCompInst.getInvocation();
    
             
    compInvocation.setLangDefaults(lo, clang::InputKind::C,TI->getTriple() , TheCompInst.getPreprocessorOpts(), clang::LangStandard::lang_c11); 
    TheCompInst.createPreprocessor(TU_Module);
    TheCompInst.createASTContext();
    
    //clang::Preprocessor preProcessor(TheCompInst.getDiagnostics(), lo, TI, SourceMgr, headerSearch);
    // Set the main file handled by the source manager to the input file.
    
    const FileEntry *FileIn = FileMgr.getFile(argv[1]);
    SourceMgr.setMainFileID(SourceMgr.createFileID(FileIn, SourceLocation(), SrcMgr::C_User));
    
    const std::unique_ptr<clang::driver::Driver> Driver(
    new clang::driver::Driver("clang-tool",llvm::sys::getDefaultTargetTriple(),TheCompInst.getDiagnostics()));
     Driver->setTitle("clang_based_tool");
     std::vector<const char*> Argv;
     Argv.emplace_back("clang-tool");
     //Argv.emplace_back("-cc1");
     //Argv.emplace_back("-target-cpu x86-64");
     //Argv.emplace_back("-resource-dir /home/kaled/clang_base/lib/clang/6.0.0");
     //Argv.emplace_back("-m64");
     Argv.emplace_back("-D__NO_CTYPE");
     Argv.emplace_back("-x");
     Argv.emplace_back("c");
     Argv.emplace_back("-Wno-unknown-attributes");
     Argv.emplace_back("-fsyntax-only");
     Argv.emplace_back(argv[1]);
     std::unique_ptr<llvm::opt::OptTable> Opts(clang::driver::createDriverOptTable());
     unsigned MissingArgIndex, MissingArgCount;
     llvm::opt::InputArgList ParsedArgs = Opts->ParseArgs(llvm::ArrayRef<const char *>(Argv).slice(1),MissingArgIndex,MissingArgCount);
     
     clang::ParseDiagnosticArgs(TheCompInst.getDiagnosticOpts(), ParsedArgs);
     mydebug("befor compilation");
    const std::unique_ptr<clang::driver::Compilation> Compilation(Driver->BuildCompilation(llvm::makeArrayRef(Argv)));
    mydebug("After compilation");
    
    TheCompInst.getDiagnosticClient().BeginSourceFile(TheCompInst.getLangOpts(), &TheCompInst.getPreprocessor());
    mydebug("After begin Source");
    // Create an AST consumer instance which is going to get called by
    // ParseAST.
    MyHolder myHolder(
            TheCompInst.getASTContext(),
            TheCompInst.getSourceManager()
    );
    if(!TheCompInst.getDiagnostics().hasErrorOccurred())
    {
         MyASTConsumer TheConsumer(TheRewriter,myHolder);
         // Parse the file to AST, registering our consumer as the AST consumer.
         mydebug("Before Parsing");
         ParseAST(TheCompInst.getPreprocessor(), &TheConsumer,TheCompInst.getASTContext());
         mydebug("After Parsing");
         TheCompInst.getDiagnosticClient().EndSourceFile();
         // At this point the rewriter's buffer should be full with the rewritten
         // file contents.
         const RewriteBuffer *RewriteBuf = TheRewriter.getRewriteBufferFor(SourceMgr.getMainFileID());
         llvm::outs() << std::string(RewriteBuf->begin(), RewriteBuf->end());        
    }
   
    return 0;

}
