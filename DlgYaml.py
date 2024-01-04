from PyQt5.QtWidgets import QDialog, QPushButton
from fusebmc_ui_gen.DlgYaml_ import Ui_DlgYaml
from fusebmc_util.fusebmcyamlparser import FuSeBMCYAMLParser
from fusebmc_util.util import GetPropertyFromFile
import os

class DlgYaml(QDialog):
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.ui = Ui_DlgYaml()
		self.ui.setupUi(self)
		self.fuSeBMCYAMLParser = None
	
	def showYaml(self, fuSeBMCYAMLParser : FuSeBMCYAMLParser) -> None:
		self.fuSeBMCYAMLParser = fuSeBMCYAMLParser
		self.ui.txtYamlFile.setText(fuSeBMCYAMLParser.yamlFile)
		self.ui.txtInput_file.setText(fuSeBMCYAMLParser.input_files)
		self.ui.cmbProperties.clear()
		for prop in fuSeBMCYAMLParser.properties:
			self.ui.cmbProperties.addItem(prop)
		self.ui.txtLanguage.setText(fuSeBMCYAMLParser.language)
		self.ui.txtData_model.setText(fuSeBMCYAMLParser.data_model)
		self.ui.txtArch.setText(fuSeBMCYAMLParser.arch)
	
	def getSelectedData(self) -> dict:
		dirPath = os.path.dirname(self.fuSeBMCYAMLParser.yamlFile)
		propFile = self.ui.cmbProperties.currentText()
		category_property, _ = GetPropertyFromFile(dirPath + '/'+ propFile)
		return {'input_file' : self.ui.txtInput_file.text(),
				'property': propFile,
				'category_property' : category_property,
				'arch':self.ui.txtArch.text()
				}