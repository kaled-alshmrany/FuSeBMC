# FuSeBMC: An Energy-Efficient Test Generator for Finding Security Vulnerabilities in C Programs
  FuSeBMC is a novel Energy-Efficient Test Generator that exploits fuzzing and BMC engines to detect security vulnerabilities in C programs. It explores and analyzes the target C program by injecting labels that guide those engines to produce test-cases. FuSeBMC also exploits a selective fuzzer to produce test-cases for the labels that fuzzing and BMC engines could not produce test-cases. Lastly, we manage each engine's execution time to improve FuSeBMC's energy consumption. As a result, FuSeBMC guides the fuzzing and BMC engines to explore more profound in the target C programs and then produce test-cases that achieve higher coverage with lower energy consumption to detect bugs efficiently. We evaluated FuSeBMC by participating in Test-Comp 2021 to test the ability of the tool in two categories of the competition, which are code coverage and bug detection. The competition results show that FuSeBMC performs well if compared to the state-of-the-art software testing tools. FuSeBMC achieved 3 awards in the Test-Comp 2021: first place in the Cover-Error category, second place in the Overall category, and third place in the Low Energy Consumption category.

For more detiles, you can read our publised paper:
https://link.springer.com/chapter/10.1007/978-3-030-71500-7_19


  <br /><br />  <br />

 * Requrments to use the tool:
 
        ESBMC 6.4
        
        Map2check v7.3.1-Flock
        
        Clang 6.0
  
        llvm 6.0.0
        
        Python 3.6.0

<br /><br />

* To compile the tool through the makefile:

 
      make clean release
      Or
      make clean debug

      Then, you will have the tool under the name "FuSeBMC_instrument"

<br /><br />
How to run it:

In order to run our fusebmc.py script,5 one must set the architecture (i.e., 32 or
64-bit), the competition strategy (i.e., k-induction, falsification, or incremental
BMC), the property file path, and the benchmark path, as:

  ./fusebmc.py [-a {32, 64}] [-p PROPERTY_FILE]
  [-s {kinduction,falsi,incr,fixed}]
  [BENCHMARK_PATH]

where -a sets the architecture, -p sets the property file path, and -s sets
the strategy (e.g., kinduction, falsi, incr, or fixed). For Test-Comp’21,
FuSeBMC uses incr for incremental BMC.


<br /><br />
<br /><br />

If you want to run just the instrument

* FuSeBMC takes 4 parameters:


       ./FuSeBMC_instrument <inputFile_> <outputFile_> <goalOutputFile_> <pathofthefuncations_> <options_>


  Or


       ./FuSeBMC_instrument <inputFile_> <outputFile_> <goalOutputFile_> <-nogoalProFunc> <options_>
 

<br /><br />


* In the folder Examples, you can find some C/C++ examples that we used in terms of testing the tool. I found useful to share it with you.

Note: all the outputs in the folders are based on the experiment on the file "rangesum 10.i" with the property coverage-branches.

<br /><br />



<br /><br />
If you want to run the tool on the benchmark of the competition "Test-Comp21", you need to put the files "competitions files" in the same directory:

1- ESBMC from https://github.com/esbmc/esbmc/releases/latest/download/ESBMC-Linux.sh

2- TestCove from https://gitlab.com/sosy-lab/test-comp/archives-2020/raw/testcomp20/2020/val_testcov.zip

3- benchexec version 2.7

4- sv-benchmarks from https://github.com/sosy-lab/sv-benchmarks/tree/testcomp20/

<br /><br />



* The output of the tool will be in the folder "fusebmc_output". You will have these files under the folder fusebmc_instrument_output" as follows:

      1- File called "instrumented.c" which has the input file + the goals labels written on the input code.<br />
      2- File called "my_goal.txt" has the number of goals.<br />
      3- Folder called "goals" has the graph files.<br />
      4- Folder called "goals_out" has the functions files if you used the option "<pathofthefuncations".<br />

<br /><br /><br />

* Other outputs of the tool will be in the folder "test-suite". You will have these files as follows:

      1- Folder called "test-suite" has the XML files.<br />
      2- Folder called "test-suite.zip" to be used for the tool TestCov.<br />

<br /><br />

* The output of the competition "Test-Comp21" will store in two folders "results" and "results-verified".
<br /><br />


Note:<br />
Release 3.6.6 do not need to compile it
