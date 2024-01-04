import os
import shutil
import shlex
import subprocess
from .tcolors import TColors
from .nonblockingstreamreader import NonBlockingStreamReader

CPA_EXE = os.path.abspath('./CPAchecker-2.1-unix/scripts/cpa.sh')
CPA_PARAMS = ['-setprop', 'witness.checkProgramHash=false','-heap', '5000m','-benchmark',
			'-setprop','cpa.predicate.memoryAllocationsAlwaysSucceed=true',
			'-witnessValidation','-timelimit', '900s', '-stats',
			#-witness /home/hosam/sdb1/FuSeBMC/fusebmc_output/sanfoundry_24-1.i_cKicAgCHtovrOLxXoxjdzJQFd/fusebmc_instrument_output/sanfoundry_24-1.i_2.graphml
			#-spec ../../sv-benchmarks/c/properties/unreach-call.prp -32 ../../sv-benchmarks/c/array-examples/sanfoundry_24-1.i
			]
def RunValidatorProc(the_args, pCwd:str = None):
	p = None
	nbsr_out = None
	nbsr_err = None
	try:
		p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=pCwd,shell=False) #bufsize=1
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

def RunCPA(p_benchmark,p_property_file,p_arch,pWitness:str,pDir:str=None):
	cmd = [CPA_EXE] + CPA_PARAMS +\
		['-witness', pWitness, '-spec', p_property_file, '-'+str(p_arch), p_benchmark]
	cmd_line = ' '.join(cmd)
	print (TColors.BOLD, '\nCPAchecker: ', cmd_line ,TColors.ENDC)
	the_args = shlex.split(cmd_line)
	RunValidatorProc(the_args,pDir)
	
	