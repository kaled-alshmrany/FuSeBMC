import xml.etree.ElementTree as ET # To parse XML
from .tcolors import TColors
from .consts import *

__graphml_base__ = '{http://graphml.graphdrawing.org/xmlns}'
__graph_tag__ = __graphml_base__ + 'graph'
__edge_tag__ = __graphml_base__ + 'edge'
__data_tag__ = __graphml_base__ + 'data'
		
class AssumptionHolder(object):
	"""Class to hold line number and assumption from ESBMC Witness."""

	def __init__(self, line, assumption):
		"""
		Default constructor.

		Parameters
		----------
		line : unsigned
			Line Number from the source file
		assumption : str
			Assumption string from ESBMC.
		"""
		assert(line >= 0)
		assert(len(assumption) > 0)
		self.line = line
		self.assumption = assumption
		#self.varName = varName
		#self.varVal = varVal

	def __str__(self):
		return "AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(self.line, self.assumption)
	
	def debugInfo(self):
		"""Print info about the object"""
		print("AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(
			self.line, self.assumption))


class AssumptionParser(object):
	"""Class to parse a witness file generated from ESBMC and create a Set of AssumptionHolder."""

	def __init__(self, witness,pIsFromMap2Check = False):
		"""
		Default constructor.

		Parameters
		----------

		witness : str
			Path to witness file (absolute/relative)
		"""
		assert(os.path.isfile(witness))
		self.__xml__ = None
		self.assumptions = list()
		self.__witness__ = witness
		self.isFromMap2Check = pIsFromMap2Check

	def __openwitness__(self):
		"""Parse XML file using ET"""
		self.__xml__ = ET.parse(self.__witness__).getroot()

	def parse(self):
		""" Iterates over all elements of GraphML and extracts all Assumptions """
		global IS_DEBUG
		

		if self.__xml__ is None:
			try:
				self.__openwitness__()
			except:
				if IS_DEBUG :
					print(TColors.FAIL,'Cannot parse file:', self.__witness__,TColors.ENDC)
		if self.__xml__ is None:
			return

		graph = self.__xml__.find(__graph_tag__)
		for node in graph:
			try:
				if(node.tag == __edge_tag__):
					startLine = 0
					assumption = ""
					for data in node:
						if data.attrib['key'] == 'startline':
							startLine = int(data.text)
						elif data.attrib['key'] == 'assumption':
							assumption = data.text
					if assumption != "":
						#print('assumption',assumption)
						#if self.isFromMap2Check:
						#	assum_l,assum_r= assumption.split(' == ')
						#	if assum_l.find('\\')== 0: assum_l = assum_l.replace('\\','',1)
						#else:
						#	assum_l,assum_r= assumption.split('=')
						#	assum_r = assum_r.replace(';','',1)
						#	if assum_r[-1] == "f" or assum_r[-1] == "l": 
						#		assum_r = assum_r[:-1]

						#TODO: handle f and l
						#_, right = pAssumptionHolder.assumption.split("=")
						
						#assum_l = assum_l.strip()
						#assum_r = assum_r.strip()		
						#print('assum_l',assum_l,len(assum_l), 'assum_r',assum_r,len(assum_r))
						self.assumptions.append(AssumptionHolder(startLine, assumption))
						#assumption : n = 2;
						#print('ass',assumption,'start',startLine)
			except:
				if IS_DEBUG :
					print(TColors.FAIL,'Cannot parse node:',TColors.ENDC)

	def debugInfo(self):
		"""Print current info about the object"""
		print("XML: {0}".format(self.__witness__))
		print("ET: {0}".format(self.__xml__))
		for assumption in self.assumptions:
			assumption.debugInfo()
			

class MetadataParser(object):
	"""Class to parse a witness file generated from ESBMC and extract all metadata from it."""

	def __init__(self, witness):
		"""
		Default constructor.

		Parameters
		----------

		witness : str
			Path to witness file (absolute/relative)
		"""
		assert(os.path.isfile(witness))
		self.__xml__ = None
		self.metadata = {}
		self.__witness__ = witness

	def __openwitness__(self):
		"""Parse XML file using ET"""
		self.__xml__ = ET.parse(self.__witness__).getroot()

	def parse(self):
		""" Iterates over all elements of GraphML and extracts all Metadata """
		if self.__xml__ is None:
			self.__openwitness__()
		graph = self.__xml__.find(__graph_tag__)
		for node in graph:
			if(node.tag == __data_tag__):
				self.metadata[node.attrib['key']] = node.text


