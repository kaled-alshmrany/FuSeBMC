#!/usr/bin/env python3
import os.path
import shlex
import subprocess

MY_FOLDER = '/home/kaled/Desktop/2020-my-projects/21-24.05.2020/FuSeBMC_v2.0/my_instrument/examples'
MY_FOLDER = '/home/kaled/Desktop/2020-my-projects/sv-benchmarks-testcomp20/c'
MY_INSTRUMENT_EXE_PATH = '/home/kaled/Desktop/2020-my-projects/21-24.05.2020/FuSeBMC_v2.0/my_instrument/my_instrument'
#SEE: https://stackoverflow.com/questions/61974126/clang-asm-with-labels-in-case-statment-gets-error-invalid-operand-for-inst
MY_COMPILER = '/home/kaled/Downloads/clang_base/bin/clang'
MY_COMPILER = 'gcc'

INSTRUMENTED_OUT_FILE = 'inst_out_78877878.c'
ORIGINAL_OBJ_FILE = 'original.o'
INSTRUMENTED_OBJ_FILE = 'ints_obj.o'
def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []
    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)
    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

def RemoveFileIfExists(fil):
    if os.path.isfile(fil): os.remove(fil)
def run_without_output(cmd_line):
    the_args = shlex.split(cmd_line)
    p = subprocess.Popen(the_args, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    p.communicate()

# Enum for size units
class SIZE_UNIT:
    BYTES = 'B'
    KB = 'KB'
    MB = 'MB'
    GB = 'GB'
def GetFileSize(file_name, unit = SIZE_UNIT.KB ):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    size_in_bytes = os.path.getsize(file_name)
    new_size = size_in_bytes
    if unit == SIZE_UNIT.KB:
        new_size = size_in_bytes/1024
    elif unit == SIZE_UNIT.MB:
        new_size =size_in_bytes/(1024*1024)
    elif unit == SIZE_UNIT.GB:
        new_size = size_in_bytes/(1024*1024*1024)
    return str(round(new_size,2)) + ' ' + str(unit)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if not os.path.isfile(MY_INSTRUMENT_EXE_PATH):
    print("my_instrument cannot be found..")
    exit(1)
subfolders, files = run_fast_scandir(MY_FOLDER, [".i"])
err_files=[]
#print(files)
try:
    for fil in files:
        RemoveFileIfExists(INSTRUMENTED_OUT_FILE)
        RemoveFileIfExists(ORIGINAL_OBJ_FILE)
        RemoveFileIfExists(INSTRUMENTED_OBJ_FILE)
        
        original_lst = [MY_COMPILER,'-c',fil,'-o',ORIGINAL_OBJ_FILE]
        instr_lst = [MY_INSTRUMENT_EXE_PATH,'--add-labels','--add-else', '--input',fil,'--output',INSTRUMENTED_OUT_FILE]
        compile_inst_lst =[MY_COMPILER,'-c',INSTRUMENTED_OUT_FILE,'-o',INSTRUMENTED_OBJ_FILE]
        run_without_output(' '.join(original_lst))
        if not os.path.isfile(ORIGINAL_OBJ_FILE):
            print(Colors.WARNING,'Cannot compile Original: ', fil, Colors.ENDC)
            continue
        run_without_output(' '.join(instr_lst))
        if not os.path.isfile(ORIGINAL_OBJ_FILE):
            print(Colors.FAIL+'Cannot compile: ', fil, Colors.ENDC)
            continue
        run_without_output(' '.join(compile_inst_lst))
        if not os.path.isfile(INSTRUMENTED_OBJ_FILE):
            err_files.append(fil)
            print(Colors.FAIL,'Cannot compile Instrumented: ', fil)
            print('---------------------------------')
            print('SIZE:',GetFileSize(fil))
            print(' '.join(instr_lst),Colors.ENDC)
            print('---------------------------------')
            continue
        print(Colors.OKGREEN ,'OK-->', fil,Colors.ENDC)
except (KeyboardInterrupt, SystemExit):
    if(len(err_files)> 0):
        print(Colors.ENDC,'Error Files', Colors.ENDC)
        for fil in err_files:
            print(fil)
    print(Colors.OKBLUE+'THANKS !!! ', Colors.ENDC)
    exit(0)
    
    
