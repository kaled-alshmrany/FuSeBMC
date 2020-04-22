# my_instrument
A tool based on ESBMC that can label all the goals in the target C code. Also, it can produce the graph file and then the XML files that we can use later to get the counterexamples values.
  <br /><br />  

 Requrments to use the tool:
 
 ESBMC 6.2
  
 Clang 6.0
  
 llvm 6.0.0

<br /><br />

To compile the tool through the makefile:

 
make clean all.


Then, you will have the tool under the name "my_instrument"

----------------------------------------------------------

my instrument takes 4 parameters:


./my_instrument <inputFile_> <outputFile_> <goalOutputFile_> <pathofthefuncations_> <options_>


  Or


 "./my_instrument <inputFile_> <outputFile_> <goalOutputFile_> <-nogoalProFunc> <options_>"
 

----------------------------------------------------------


In the folder Examples, you can find some C/C++ examples that we used in terms of testing the tool. I found useful to share it with you.





The output of the tool will be in the folder "output". You will have these files as follows:


1- File called "instrumented.c" which has the input file + the goals labels written on the input code.

2- File called "my_goal.txt" has the number of goals.

3- Folder called "goals" has the graph files.

4- Folder called "test-suite" has the XML files.

5- Folder called "goals_out" has the functions files if you used the option "<pathofthefuncations".



----------------------------------------------------------



Note:
The tool is still under testing.
