import os
import shutil
import shlex
import subprocess

from .consts import *
from .tcolors import TColors
from.util import *
from .nonblockingstreamreader import NonBlockingStreamReader

#TESTCOV_EXE = './val_testcov/testcov/bin/testcov'
#TESTCOV_EXE ='./val_testcov_3.5/testcov/bin/testcov'
TESTCOV_EXE = './test-suite-validator/bin/testcov'
#TESTCOV_PARAMS = ['--no-runexec','--use-gcov','-64']
#TESTCOV_PARAMS= ['--no-runexec','--use-gcov','--cpu-cores','0', '--verbose', '--no-plots','--reduction','BY_ORDER','--reduction-output','test-suite']
#TESTCOV_PARAMS= ['--no-runexec', '--no-isolation', '--memlimit', '6GB', '--timelimit-per-run', '3', '--cpu-cores', '0', '--verbose', '--no-plots','--reduction', 'BY_ORDER','--reduction-output','test-suite']
TESTCOV_PARAMS = ['--no-isolation','--memlimit', '6GB','--timelimit-per-run', '100', '--cpu-cores', '0','--no-plots','--reduction', 'BY_ORDER', '--reduction-output','test-suite']#'--verbose'


def RunTestCov(p_benchmark,p_property_file,p_arch,p_dir,isVerbose = False):
	'''
	p_dir: must contain 'test-suite' dir; will be used as output dir.
	'''
	testSuite_dir= p_dir+'/test-suite'
	zipDir_l = os.path.abspath(p_dir+'/test-suite.zip')
	RemoveFileIfExists(zipDir_l)
	os.system('zip -j -r '+zipDir_l+' '+ testSuite_dir)
	#runWithoutTimeoutEnabled(' '.join(['zip', '-j',zipDir_l,' ',os.path.join(TESTSUITE_DIR,'*.xml')]), WRAPPER_OUTPUT_DIR, True)
	print("\nValidating Test-Cases ...\n")
	cov_test_exe_abs=os.path.abspath(TESTCOV_EXE)
	cov_test_cmd =[cov_test_exe_abs]
	cov_test_cmd.extend(TESTCOV_PARAMS)
	if isVerbose : cov_test_cmd.append('--verbose')
	test_suite_dir_zip_abs=os.path.abspath(zipDir_l)
	property_file_abs = os.path.abspath(p_property_file)
	sourceForTestCov = p_dir + '/' + os.path.basename(p_benchmark)
	sourceForTestCov = os.path.abspath(sourceForTestCov)
	testCovOutputDir = os.path.abspath(p_dir + '/output_cov')
	cov_test_cmd.extend(['--output', testCovOutputDir])
	print('sourceForTestCov',sourceForTestCov)
	shutil.copyfile(p_benchmark ,sourceForTestCov)
	cov_test_cmd.extend(['-'+str(p_arch),'--test-suite' ,test_suite_dir_zip_abs , '--goal' ,property_file_abs , sourceForTestCov])
	#runWithoutTimeoutEnabled(' '.join(cov_test_cmd), INSTRUMENT_OUTPUT_DIR, True)
	cmd_line = ' '.join(cov_test_cmd)
	print (TColors.BOLD, '\nCommand: ', cmd_line ,TColors.ENDC)
	the_args = shlex.split(cmd_line)
	p = None
	nbsr_out = None
	nbsr_err = None
	try:
		p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=p_dir,shell=False) #bufsize=1
		nbsr_out = NonBlockingStreamReader(p.stdout)
		nbsr_err = NonBlockingStreamReader(p.stderr)
		while nbsr_err.hasMore():
			err = nbsr_err.readline(1)
			if err: print(err)
		while nbsr_out.hasMore():
			output = nbsr_out.readline(1)
			if output: print(output)
	except KeyboardInterrupt:pass
	if p is not None:
		try:
			p.terminate()
			while nbsr_out is not None and  nbsr_out.hasMore():
				output = nbsr_out.readline(1) # second 0.01
				if output: print(output)
			while nbsr_err is not None and nbsr_err.hasMore():
				err = nbsr_err.readline(1) # 0.01
				if err: print(err)
		except:
			pass

