import os
import yaml
class FuSeBMCYAMLParser:
	def __init__(self):
		self.yamlFile = None
		self.input_files = None
		self.properties = []
		self.language = None
		self.data_model = None
		self.arch = None

	def clear(self) -> None:
		self.yamlFile = None
		self.input_files = None
		self.properties = []
		self.language = None
		self.data_model = None
		self.arch = None
	
	def parse(self, p_yamlFile : str) -> None:
		if self.yamlFile  is not None: self.clear()
		self.yamlFile = p_yamlFile
		dirPath = os.path.dirname(p_yamlFile)
		with open(p_yamlFile, 'r') as stream:
			yamlDict = yaml.safe_load(stream)
			#print(yamlDict)
			#print(type(yamlDict))
			self.input_files = yamlDict.get('input_files')
			if self.input_files is not None and not os.path.isabs(self.input_files):
				self.input_files = os.path.abspath(dirPath+'/'+ self.input_files)
			lstProp = yamlDict.get('properties')
			if lstProp is not None and isinstance(lstProp, list):
				for l_propDict in lstProp:
					l_property_file = l_propDict.get('property_file')
					if l_property_file is not None: self.properties.append(l_property_file)
			optionsDict = yamlDict.get('options')
			if optionsDict is not None and isinstance(optionsDict, dict):
				self.language = optionsDict.get('language')
				self.data_model = optionsDict.get('data_model')
				if self.data_model == 'ILP32' :
					self.arch = '32'
				elif self.data_model == 'LP64' :
					self.arch = '64'
	def print_str(self) -> None:
		print('yamlFile:', self.yamlFile)
		print('input_files:', self.input_files)
		print('properties:', self.properties)
		print('language:', self.language)
		print('data_model:', self.data_model)
		print('arch:', self.arch )
