# FuSeBMC
* A tool based on ESBMC that can label all the goals in the target C code. Also, it can produce the graph file and then the XML files that we can use later to get the counterexamples values.
* FuSeBMC can participate in a competition such as "Test-Comp20" and compare the results with state-of-the-art testing tools.
* FuSeBMC can analyze the target file and then put the labels "GOAL_#" in this target file so the tool after can use it to produce the counterexample that will reach us to that line in the code.
* FuSeBMC can help us to get the counterexamples for each path in the target file because of the method I used in the tool.
* FuSeBMC uses several technics such as Fuzzing and BMC.
* FuSeBMC is now able to participate in the categories "Cover-Branches" and "Cover-error" in the competition "Test-Comp20".
  <br /><br />  <br />

 * Requrments to use the tool:
 
        ESBMC 6.2
  
        Clang 6.0
  
        llvm 6.0.0
        
        Python 3.6.0

<br /><br />

* To compile the tool through the makefile:

 
      make clean release
      Or
      make clean debug

      Then, you will have the tool under the name "my_instrument"

<br /><br />
How to run it:


./esbmc-wrapper.py -p ./properties/coverage-branches.prp -s incr ./examples/rangesum10.i


<br /><br />


<br /><br />

If you want to run just the instrument

* FuSeBMC takes 4 parameters:


       ./my_instrument <inputFile_> <outputFile_> <goalOutputFile_> <pathofthefuncations_> <options_>


  Or


       ./my_instrument <inputFile_> <outputFile_> <goalOutputFile_> <-nogoalProFunc> <options_>
 

<br /><br />


* In the folder Examples, you can find some C/C++ examples that we used in terms of testing the tool. I found useful to share it with you.

Note: all the outputs in the folders are based on the experiment on the file "rangesum 10.i" with the property coverage-branches.

<br /><br />



<br /><br />
If you want to run the tool on the benchmark of the competition "Test-Comp20", you need to put the files "competitions files" in the same directory:

1- ESBMC from https://github.com/esbmc/esbmc/releases/latest/download/ESBMC-Linux.sh

2- TestCove from https://gitlab.com/sosy-lab/test-comp/archives-2020/raw/testcomp20/2020/val_testcov.zip

3- benchexec version 2.7

4- sv-benchmarks from https://github.com/sosy-lab/sv-benchmarks/tree/testcomp20/

<br /><br />



* The output of the tool will be in the folder "my_instrument_outpt". You will have these files as follows:

      1- File called "instrumented.c" which has the input file + the goals labels written on the input code.<br />
      2- File called "my_goal.txt" has the number of goals.<br />
      3- Folder called "goals" has the graph files.<br />
      4- Folder called "goals_out" has the functions files if you used the option "<pathofthefuncations".<br />

<br /><br /><br />

* Other outputs of the tool will be in the folder "test-suite". You will have these files as follows:

      1- Folder called "test-suite" has the XML files.<br />
      2- Folder called "test-suite.zip" to be used for the tool TestCov.<br />

<br /><br />

* The output of the competition "Test-Comp20" will store in two folders "results" and "results-verified".
<br /><br />


Note:<br />
The tool is still under testing.
