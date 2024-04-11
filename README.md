# FuSeBMC v4: Smart Seed Generation for Hybrid Fuzzing
FuSeBMC is a test generator for finding security vulnerabilities in C programs. In ealair work (version 3), we described a previous version that incrementally injected labels to guide Bounded Model Checking (BMC) and Evolutionary Fuzzing engines to produce test cases for code coverage and bug finding. Today, we introduce an improved version of FuSeBMC that utilizes both engines to produce smart seeds. First, the engines run with a short time limit on a lightly instrumented version of the program to produce the seeds. The BMC engine is particularly useful in producing seeds that can pass through complex mathematical guards. Then, FuSeBMC runs its engines with extended time limits using the smart seeds created in the previous round. FuSeBMC manages this process in two main ways using its Tracer subsystem. Firstly, it uses shared memory to record the labels covered by each test case. Secondly, it evaluates test cases, and those of high impact are turned into seeds for subsequent test fuzzing. We evaluated FuSeBMC by participating in Test-Comp 2022 to test the ability of the tool in two categories of the competition, which are code coverage and bug detection. The Test-Comp 2022 results show that we significantly increased our code coverage score from last year, outperforming all tools in all categories. During years (2021 & 2022), FuSeBMC achieved 6 awards (4 Gold🥇 Medals, 1 Silver🥈 Medal, 1 Bronze🥉 Medal).


FuSeBMC v4 files:
https://gitlab.com/sosy-lab/test-comp/archives-2022/-/raw/main/2022/FuSeBMC.zip?inline=false

The results of FuSeBMC in Test-Comp 2022 are available in this link:
https://test-comp.sosy-lab.org/2022/results/results-verified/

All files to reproducing Test-Comp Results:
https://test-comp.sosy-lab.org/2021/systems.php

Presentation and tutorial:
https://drive.google.com/drive/folders/1XMnNkAGP1e6ZuoygBTEaanM80I_QRe_g?usp=sharing

For more details, we recommend to read our published papers:

1- https://arxiv.org/abs/2206.14068 (2023)

2- https://link.springer.com/chapter/10.1007/978-3-030-99429-7_19 (2022)

3- https://link.springer.com/chapter/10.1007/978-3-030-79379-1_6 (2021)

4- https://link.springer.com/chapter/10.1007/978-3-030-71500-7_19 (2020)


  <br /><br />

 * Requrments to use the tool:
 
        ESBMC 6.4 (included in zip file)
 
        Map2check v7.3.1-Flock (included  in zip file)
        
        Clang 6.0
  
        llvm 6.0.0
        
        Python 3.6.0
        
        AFL 2.57

<br /><br />

* To compile the tool through the FuSeBMC/FuSeBMC_instrument/make-release.sh:

 
      make clean release
      Or
      make clean debug

      Then, you will have the tool under the name "FuSeBMC_instrument"

<br /><br />
How to run it:

In order to run our FuSeBMC, all you need is to use our script "fusebmc.py," one must set the architecture (i.e., 32 or 64-bit), the competition strategy (i.e., k-induction, falsification, or incremental BMC), the property file path, and the benchmark path, as:

     ./fusebmc.py [-a {32, 64}] [-p PROPERTY_FILE] [-s {kinduction,falsi,incr,fixed}] [BENCHMARK_PATH]

where -a sets the architecture, -p sets the property file path, and -s sets the strategy (e.g., kinduction, falsi, incr, or fixed). For Test-Comp’21, FuSeBMC uses incr for incremental BMC.
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
If you want to run the tool on the benchmark of the competition "Test-Comp21", you need to put the files "competitions files" in the same directory. However, you need to run FuSeBMC on Benchexec provided by Test-Comp 21. In order to participate at Test-Comp, a tool-info module in the BenchExec repository is necessary. The experiments were conducted on the server of Test-Comp 2021. Each run was limited to 8 processing units, 15 GB of memory, and 15 min of CPU time. The test suite validation was limited to 2 processing units, 7 GB of memory, and 5 min of CPU time. Also, the machine had the following specification of the test node was: one Intel Xeon E3-1230 v5 CPU, with 8 processing units each, a frequency of 3.4 GHz, 33 GB of RAM, and a GNU/Linux operating system(x86-64-Linux, Ubuntu 20.04 with Linux kernel 5.4).

1- ESBMC from https://github.com/esbmc/esbmc/releases/download/v7.5/esbmc-linux.zip

2- TestCove from https://gitlab.com/sosy-lab/test-comp/archives-2020/raw/testcomp20/2020/val_testcov.zip

3- benchexec version 3.6 from https://doi.org/10.5281/zenodo.4317433

4- sv-benchmarks from https://github.com/sosy-lab/sv-benchmarks/tree/testcomp21/

5- tool-info from https://gitlab.com/sosy-lab/test-comp/bench-defs/blob/testcomp21/benchmark-defs/FuSeBMC.xml

6- Reproducing Test-Comp Results from https://test-comp.sosy-lab.org/2021/systems.php

To reproduce Test-Comp 2021' results, follow the instruction in the file "instructions&command_lines.TXT"

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


* The output of the competition "Test-Comp21" will store in two folders "results" and "results-verified".
<br /><br />




# Acknowledgments

The Institute of Public Administration - IPA - Saudi Arabia (https://www.ipa.edu.sa/en-us/Pages/default.aspx) and the ScorCH project (https://lnkd.in/eSUZFwT) support the FuSeBMC development.
