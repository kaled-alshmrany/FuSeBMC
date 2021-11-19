import sys
from .tcolors import TColors
from .consts import *

class InputType:
	unkonwn = 0,
	_char = 1
	_uchar = 2
	_short = 3
	_ushort = 4
	_int = 5
	_uint = 6
	_long = 7
	_ulong = 8
	_longlong = 9
	_ulonglong = 10
	_float = 11
	_double = 12
	_bool = 13
	_string = 14
	

	@staticmethod
	def GetInputTypeForNonDetFunc(func):
		global IS_DEBUG
		
		if func == '__VERIFIER_nondet_char': return InputType._char
		if func == '__VERIFIER_nondet_uchar' or func == '__VERIFIER_nondet_u8' or \
			func == '__VERIFIER_nondet_unsigned_char':
			return InputType._uchar
		if func == '__VERIFIER_nondet_short': return InputType._short
		if func == '__VERIFIER_nondet_ushort' or func == '__VERIFIER_nondet_u16':
			return InputType._ushort
		if func == '__VERIFIER_nondet_int': return InputType._int
		if func == '__VERIFIER_nondet_uint' or func == '__VERIFIER_nondet_size_t' or \
			func == '__VERIFIER_nondet_u32' or func == '__VERIFIER_nondet_U32' or func == '__VERIFIER_nondet_unsigned':
			return InputType._uint
		if func == '__VERIFIER_nondet_long': return InputType._long
		if func == '__VERIFIER_nondet_ulong' or func == '__VERIFIER_nondet_pointer':
			return InputType._ulong
		if func == '__VERIFIER_nondet_longlong': return InputType._longlong
		if func == '__VERIFIER_nondet_ulonglong': return InputType._ulonglong
		if func == '__VERIFIER_nondet_float': return InputType._float
		if func == '__VERIFIER_nondet_double': return InputType._double
		if func == '__VERIFIER_nondet_bool': return InputType._bool
		if func == '__VERIFIER_nondet_string': return InputType._string
		if IS_DEBUG:
			print(TColors.FAIL,'func:', func , 'has no type...',TColors.ENDC)
			sys.exit(0)
		return InputType.unkonwn
	@staticmethod
	def GetAs_C_DataType(inputType):
		if inputType == InputType.unkonwn: return ''
		if inputType == InputType._char: return 'char'
		if inputType == InputType._uchar: return 'unsigned char'
		if inputType == InputType._short : return 'short'
		if inputType == InputType._ushort : return 'unsigned short'
		if inputType == InputType._int : return 'int'
		if inputType == InputType._uint : return 'unsigned int'
		if inputType == InputType._long: return 'long'
		if inputType == InputType._ulong : return 'unsigned long'
		if inputType == InputType._longlong : return 'long long'
		if inputType == InputType._ulonglong : return 'unsigned long long'
		if inputType == InputType._float : return 'float'
		if inputType == InputType._double: return 'double'
		if inputType == InputType._bool : return '_Bool'
		if inputType == InputType._string : return 'string'

	@staticmethod
	def GeSizeForDataType(inputType,p_arch):
		if inputType == InputType.unkonwn: return FuSeBMCFuzzerLib_COVERBRANCHES_BYTES_PER_NUMBER
		if inputType == InputType._char: return 1
		if inputType == InputType._uchar: return 1
		if inputType == InputType._short : return 2
		if inputType == InputType._ushort : return 2
		if inputType == InputType._int : return 4
		if inputType == InputType._uint : return 4
		if inputType == InputType._long:
			if p_arch == 32: return 4
			else : return 8
		if inputType == InputType._ulong : 
			if p_arch == 32: return 4
			else : return 8
		if inputType == InputType._longlong : return 8
		if inputType == InputType._ulonglong : return 8
		if inputType == InputType._float : return 4
		if inputType == InputType._double: return 8
		if inputType == InputType._bool : return 1
		if inputType == InputType._string :
			if IS_DEBUG:
				print(TColors.FAIL,'dont call GeSizeForDataType for String..',TColors.ENDC)
				sys.exit(0)
			return FuSeBMCFuzzerLib_COVERBRANCHES_BYTES_PER_NUMBER
		
		return FuSeBMCFuzzerLib_COVERBRANCHES_BYTES_PER_NUMBER
	
	@staticmethod
	def IsUnSigned(inputType):
		return inputType == InputType._uchar or inputType == InputType._uint \
			or inputType == InputType._ushort or inputType == InputType._ulong \
			or inputType == InputType._ulonglong

