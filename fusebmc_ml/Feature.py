#from fusebmc_util.util import HandleException
import xml.etree.ElementTree as ET

class ModelType:
	DTC = 0
	SVC = 1
	NRR = 2
	MULTI_MODEL = 3

class Feature:
	NONE = 0
	ExtractFeaturesOnly = 1
	PredicateParams = 2

	def __init__(self):
		self.forCount = 0
		self.forMaxDepth = 0
		self.forDepthAvg = 0
		self.whileCount = 0.0
		self.whileMaxDepth = 0
		self.whileDepthAvg = 0.0
		self.whileInfiniteCount = 0
		self.whileInfiniteWithNonDetCallCount = 0
		self.doCount = 0
		self.doMaxDepth = 0
		self.doDepthAvg = 0.0
		self.doInfiniteCount = 0
		self.ifCount = 0
		self.ifMaxDepth = 0
		self.ifDepthAvg = 0.0
		self.nestedIfCount = 0
		self.elseCount = 0
		self.elseDepthAvg = 0.0
		self.nonDetCallCount = 0
		self.nonDetCallDepthAvg = 0.0
		self.hasConcurrency = 0
		self.hasNonDetCallInLoop = 0
		
		self.name = ''
		self.wallCpuTime = 0
		self.origScore = 0.0
		self.ourScore = 0.0
		self.ClassifyClass = 5 # classes = 0,1,2,3,4,5
	
	def parseFromElement(self,p_rootXML: ET.Element)-> None:
		if p_rootXML is None : return
		from fusebmc_util.util import HandleException
		try:
			elemFeatures = p_rootXML.find('features')
			if elemFeatures is not None:
				self.forCount = int(elemFeatures.find('forCount').text)
				self.forMaxDepth = int(elemFeatures.find('forMaxDepth').text)
				self.forDepthAvg = float(elemFeatures.find('forDepthAvg').text)
				self.whileCount = int(elemFeatures.find('whileCount').text)
				self.whileMaxDepth = int(elemFeatures.find('whileMaxDepth').text)
				self.whileDepthAvg = float(elemFeatures.find('whileDepthAvg').text)
				self.whileInfiniteCount = int(elemFeatures.find('whileInfiniteCount').text)
				self.whileInfiniteWithNonDetCallCount = int(elemFeatures.find('whileInfiniteWithNonDetCallCount').text)
				self.doCount = int(elemFeatures.find('doCount').text)
				self.doMaxDepth = int(elemFeatures.find('doMaxDepth').text)
				self.doDepthAvg = float(elemFeatures.find('doDepthAvg').text)
				self.doInfiniteCount = int(elemFeatures.find('doInfiniteCount').text)
				self.ifCount = int(elemFeatures.find('ifCount').text)
				self.ifMaxDepth = int(elemFeatures.find('ifMaxDepth').text)
				self.ifDepthAvg = float(elemFeatures.find('ifDepthAvg').text)
				self.nestedIfCount = int(elemFeatures.find('nestedIfCount').text)
				self.elseCount = int(elemFeatures.find('elseCount').text)
				self.elseDepthAvg = float(elemFeatures.find('elseDepthAvg').text)
				self.nonDetCallCount = int(elemFeatures.find('nonDetCallCount').text)
				self.nonDetCallDepthAvg = float(elemFeatures.find('nonDetCallDepthAvg').text)
				self.hasConcurrency = int(elemFeatures.find('hasConcurrency').text)
				self.hasNonDetCallInLoop = int(elemFeatures.find('hasNonDetCallInLoop').text)
		except Exception as ex:
			HandleException(ex)
	
	def parseFromBenchExecXMLColumn(self,col: ET.Element) -> None:
		from fusebmc_util.util import HandleException
		try:
			title = col.get('title')
			if title is None: return
			val = col.get('value')
			if val is None: return
			if title == "FuseBMC_doCount": self.doCount = int(val)
			elif title == "FuseBMC_doDepthAvg": self.doDepthAvg = float(val)
			elif title == "FuseBMC_doInfiniteCount": self.doInfiniteCount = int(val)
			elif title == "FuseBMC_doMaxDepth": self.doMaxDepth = int(val)
			elif title == "FuseBMC_elseCount": self.elseCount = int(val)
			elif title == "FuseBMC_elseDepthAvg": self.elseDepthAvg = float(val)
			elif title == "FuseBMC_forCount": self.forCount = int(val)
			elif title == "FuseBMC_forDepthAvg": self.forDepthAvg = float(val)
			elif title == "FuseBMC_forMaxDepth": self.forMaxDepth = int(val)
			elif title == "FuseBMC_hasConcurrency": self.hasConcurrency = int(val)
			elif title == "FuseBMC_hasNonDetCallInLoop": self.hasNonDetCallInLoop = int(val)
			elif title == "FuseBMC_ifCount": self.ifCount = int(val)
			elif title == "FuseBMC_ifDepthAvg": self.ifDepthAvg = float(val)
			elif title == "FuseBMC_ifMaxDepth": self.ifMaxDepth = int(val)
			elif title == "FuseBMC_nestedIfCount": self.nestedIfCount = int(val)
			elif title == "FuseBMC_nonDetCallCount": self.nonDetCallCount = int(val)
			elif title == "FuseBMC_nonDetCallDepthAvg": self.nonDetCallDepthAvg = float(val)
			elif title == "FuseBMC_whileCount": self.whileCount = int(val)
			elif title == "FuseBMC_whileDepthAvg": self.whileDepthAvg = float(val)
			elif title == "FuseBMC_whileInfiniteCount": self.whileInfiniteCount = int(val)
			elif title == "FuseBMC_whileInfiniteWithNonDetCallCount": self.whileInfiniteWithNonDetCallCount = int(val)
			elif title == "FuseBMC_whileMaxDepth": self.whileMaxDepth = int(val)
			else:
				raise Exception(title, 'is not valid Feature for FuSeBMC.')

			
		except Exception as ex:
			HandleException(ex)
	
	def toList(self)-> list:
		return [self.forCount,
				self.forMaxDepth,
				self.forDepthAvg,
				self.whileCount,
				self.whileMaxDepth,
				self.whileDepthAvg,
				self.whileInfiniteCount,
				self.whileInfiniteWithNonDetCallCount,
				self.doCount,
				self.doMaxDepth,
				self.doDepthAvg,
				self.doInfiniteCount,
				self.ifCount,
				self.ifMaxDepth,
				self.ifDepthAvg,
				self.nestedIfCount,
				self.elseCount,
				self.elseDepthAvg,
				self.nonDetCallCount,
				self.nonDetCallDepthAvg,
				self.hasConcurrency,
				self.hasNonDetCallInLoop,
				]

	@staticmethod
	def getColumnsHeader()-> list:
		return ['forCount',
				'forMaxDepth',
				'forDepthAvg',
				'whileCount',
				'whileMaxDepth',
				'whileDepthAvg',
				'whileInfiniteCount',
				'whileInfiniteWithNonDetCallCount',
				'doCount',
				'doMaxDepth',
				'doDepthAvg',
				'doInfiniteCount',
				'ifCount',
				'ifMaxDepth',
				'ifDepthAvg',
				'nestedIfCount',
				'elseCount',
				'elseDepthAvg',
				'nonDetCallCount',
				'nonDetCallDepthAvg',
				'hasConcurrency',
				'hasNonDetCallInLoop',
				]
		
	def printOut(self)-> None:
		print('=========== FEATURE BEGIN ===========')
		print('FuseBMC_forCount:', self.forCount)
		print('FuseBMC_forMaxDepth:', self.forMaxDepth)
		print('FuseBMC_forDepthAvg:', self.forDepthAvg)
		print('FuseBMC_whileCount:', self.whileCount)
		print('FuseBMC_whileMaxDepth:', self.whileMaxDepth)
		print('FuseBMC_whileDepthAvg:', self.whileDepthAvg)
		print('FuseBMC_whileInfiniteCount:', self.whileInfiniteCount)
		print('FuseBMC_whileInfiniteWithNonDetCallCount:', self.whileInfiniteWithNonDetCallCount)
		print('FuseBMC_doCount:', self.doCount)
		print('FuseBMC_doMaxDepth:', self.doMaxDepth)
		print('FuseBMC_doDepthAvg:', self.doDepthAvg)
		print('FuseBMC_doInfiniteCount:', self.doInfiniteCount)
		print('FuseBMC_ifCount:', self.ifCount)
		print('FuseBMC_ifMaxDepth:', self.ifMaxDepth)
		print('FuseBMC_ifDepthAvg:', self.ifDepthAvg)
		print('FuseBMC_nestedIfCount:', self.nestedIfCount)
		print('FuseBMC_elseCount:', self.elseCount)
		print('FuseBMC_elseDepthAvg:', self.elseDepthAvg)
		print('FuseBMC_nonDetCallCount:', self.nonDetCallCount)
		print('FuseBMC_nonDetCallDepthAvg:', self.nonDetCallDepthAvg)
		print('FuseBMC_hasConcurrency:', self.hasConcurrency)
		print('FuseBMC_hasNonDetCallInLoop:', self.hasNonDetCallInLoop)
		print('=========== FEATURE END   ===========')
