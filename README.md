# my_instrument
A tool based on ESBMC that can label all the goals in the target C code. Also, it can produce the graph file and then the XML files that we can use later to get the counterexamples values.

 Requrments to use the tool:
 ESBMC 6.2
 Clang 6.0
 llvm 6.0.0

To compile the tool through the makefile:

make clean all

Then, you will have the tool under the name "my_instrument"

my instrument takes 4 parameters:

"./my_instrument <inputFile> <outputFile> <goalOutputFile> <pathofthefuncations> <options>"
  
  Or
  
 "./my_instrument <inputFile> <outputFile> <goalOutputFile> <-nogoalProFunc> <options>"
 
 In the folder Examples, you can find some C/C++ examples that we used in terms of testing the tool. I found useful to share it with you.

Note:
The tool is still under testing.
