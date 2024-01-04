#!/usr/bin/env python3
from PyQt5.QtCore import *
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow , QMessageBox, QFileDialog , QCheckBox ,\
	QSpinBox , QDialog, QTableWidgetItem, QErrorMessage

from fusebmc_ui_gen.MainWindow_ import Ui_MainWindow
from DlgYaml import DlgYaml
import sys
import shlex
import subprocess
import signal
from fusebmc_util.nonblockingstreamreader import NonBlockingStreamReader
from fusebmc_util.util import *
import glob
import time
import io
from fusebmc_util.fusebmcyamlparser import FuSeBMCYAMLParser
import xml.etree.ElementTree as ET
import json
from fusebmc_util.goalsorting import GoalSorting



#from fusebmc import *
MY_DEBUG = not True
class Worker(QObject):
	finished = pyqtSignal()
	intReady = pyqtSignal(int)
	dataFromFuSeBMCReady = pyqtSignal(str)
	
	def __init__(self, fuSeBMCMainWindow, lstCommand: list):
		super().__init__()
		self.fuSeBMCMainWindow = fuSeBMCMainWindow
		self.proc = None
		self.process = None
		self.lstCommand = lstCommand


	@pyqtSlot()
	def procCounter(self): # A slot takes no params
		'''for i in range(1, 100):
			time.sleep(1)
			print(i)
			self.intReady.emit(i)
		'''
		
		
		
		#RunFuSeBMC();
		self.proc = None
		#nbsr_out = None
		try:
			#self.proc = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd='./',shell=False,text=False,bufsize = None) #bufsize=1 , preexec_fn=limit_virtual_memory
			'''nbsr_out = NonBlockingStreamReader(self.proc.stdout)
			while nbsr_out.hasMore():
				output = nbsr_out.readline(None) # second 0.01
				if output:
					print(output)
					sys.stdout.flush()
			'''
			'''while True:
				line = self.proc.stdout.readline()
				if not line: break
				line_de = line.rstrip()
				print(line_de)
				sys.stdout.flush()'''
			
			#for line in io.TextIOWrapper(self.proc.stdout, encoding="utf-8"):
			#	print(line)
			self.process = QProcess()
			self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
			self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
			self.process.finished.connect(self.onFinished)
			self.process.start('./fusebmc.py', self.lstCommand)
			sys.stdout.flush()
		except Exception as ex:
			pass
			print('ERRRRRR', ex)
		#QMessageBox.information(self, "Info", "Connected....")
		if self.proc is not None:
			try:
				#if p.poll() is None: # proc still working
					#os.killpg(os.getpgid(p.pid), signal.SIGTERM)
					#os.killpg(os.getpgid(p.pid), signal.SIGKILL)
				self.proc.terminate()
				time.sleep(0.5)
				self.proc.kill()
				#print('Killed......')
			except:
				#print('EXXXXXXXX')
				#print(ex)
				pass
		#self.finished.emit()
		print('finish')
	def onReadyReadStandardError(self):
		error = self.process.readAllStandardError().data().decode()
		print(error)
		if error is not None and error.startswith('<'):
			self.dataFromFuSeBMCReady.emit(error)
		
		#self.errorSignal.emit(error)

	def onReadyReadStandardOutput(self):
		result = self.process.readAllStandardOutput().data().decode()
		print(result)
		
		#self.outputSignal.emit(result)
	def onFinished(self, exitCode, exitStatus):
		print('FFFFFFinish')
		self.process = None
		self.finished.emit()
	
	def SendTermSignal(self):
		try:
			if self.process is not None:
				#self.process.send_signal(signal.SIGINT)
				#self.process.terminate()
				if self.process.state() == QProcess.ProcessState.Running:
					os.kill(self.process.pid(), signal.SIGINT)
		except Exception as ex:
			print('Errrorrrr', ex)

class FuSeBMCMainWindow (QMainWindow, Ui_MainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.lblParametersGenerated.setVisible(False)
		self.lstCommand, self.lstSpecific, self.lstXMLParams , self.strXMLParams = [],[],[],''
		self.pushButton.clicked.connect(self.pushButton_clicked)
		self.btnOpenBenchmark.clicked.connect(self.btnOpenBenchmark_clicked)
		self.btnExec.clicked.connect(self.btnExec_clicked)
		self.btnStop.clicked.connect(self.btnStop_clicked)
		self.btnOpenResultDir.clicked.connect(self.btnOpenResultDir_clicked)
		self.lstProperty = []
		for fil in glob.glob("./properties/*.prp"):
			category_property, _ = GetPropertyFromFile(fil)
			if category_property:
				self.cmbProperty.addItem(fil)
				self.lstProperty.append(category_property)
		self.cmbProperty.currentIndexChanged.connect(self.cmbPropertyCurrentIndexChanged)
		
		
		for strategy in ['incr', 'kinduction', 'falsi', 'fixed']:
			self.cmbStrategy.addItem(strategy)
		self.cmbStrategy.currentIndexChanged.connect(self.cmbStrategyCurrentIndexChanged)
		for arch in ['64', '32']:
			self.cmbArch.addItem(arch)
		'''
		self.txtBenchmark.setText('sv-benchmarks/c/seq-mthreaded/pals_lcr.4.ufo.BOUNDED-8.pals.c')
		self.cmbProperty.setCurrentIndex(4)
		'''
		#kaled
		'''self.txtBenchmark.setText('sv-benchmarks/c/reducercommutativity/rangesum.i')
		self.cmbProperty.setCurrentIndex(5)
		self.cmbArch.setCurrentIndex(1)
		'''
		#'''
		self.txtBenchmark.setText('sv-benchmarks/c/termination-crafted/4BitCounterPointer.c')
		self.cmbProperty.setCurrentIndex(6)
		self.cmbArch.setCurrentIndex(0)
		#'''
		
		self.worker = None
		self.thread = None
		self.chkCoverBrancherFuzzer1.toggled.connect(self.chkCoverBrancherFuzzer1Toggled)
		self.chkCoverBrancherFuzzer2.toggled.connect(self.chkCoverBrancherFuzzer2Toggled)
		self.cat = 0
		self.tblCoverBranchesResult.resizeColumnsToContents()
		
		self.lstGoalSorting = [GoalSorting.DEPTH_THEN_TYPE , GoalSorting.TYPE_THEN_DEPTH , GoalSorting.SEQUENTIAL]
		for gSorting in self.lstGoalSorting:
			self.cmbGoalSorting.addItem(GoalSorting.toString(gSorting))
		
		self.chkErrorCallFuzzer1.toggled.connect(self.chkErrorCallFuzzer1Toggled)
		self.chkErrorCallFuzzer2.toggled.connect(self.chkErrorCallFuzzer2Toggled)
		self.chkECRunESBMCTwice.toggled.connect(self.chkECRunESBMCTwiceToggled)
		self.chkECHandleInfiniteWhileLoop.toggled.connect(self.chkECHandleInfiniteWhileLoopToggled)
		#self.label_4.setText("<a href='/home/hosam/sdb1/FuSeBMC/tutorial/'>Open Project Folder</a>")
		self.btnGenerateCmd.clicked.connect(self.btnGenerateCmd_clicked)
		
		self.chkCBHandleInfiniteWhileLoop.toggled.connect(self.chkCBHandleInfiniteWhileLoopToggled)
		self.chkCBHandleSelectiveInput.toggled.connect(self.chkCBHandleSelectiveInputToggled)
		
		self.chkECHandleSelectiveInput.toggled.connect(self.chkECHandleSelectiveInputToggled)
		self.chkCBUnlimitedKStep.toggled.connect(self.chkCBUnlimitedKStepToggled)
		
		self.chkECUnlimitedKStep.toggled.connect(self.chkECUnlimitedKStepToggled)
		
		self.chkTUnlimitedKStep.toggled.connect(self.chkTUnlimitedKStepToggled)
		#self.chkTUnlimitedContextBound.toggled.connect(self.chkTUnlimitedContextBoundToggled)
		
		self.cmbML.addItem('None')
		self.cmbML.addItem('Extract Features only')
		self.cmbML.addItem('Predicate FuSeBMC Paramerters')
		self.cmbML.currentIndexChanged.connect(self.cmbMLCurrentIndexChanged)
		
		for model in ['Decision Tree Classifier','C-Support Vector Classification','Multi-layer Perceptron regressor']:
			self.cmbModel.addItem(model)
		
		if not MY_DEBUG:
			self.pushButton.hide()
		#kaled:
		self.cmbML.setCurrentIndex(1)
		
	def pushButton_clicked(self):
		return
		fuSeBMCYAMLParser = FuSeBMCYAMLParser()
		fuSeBMCYAMLParser.parse('/home/hosam/sdb1/FuSeBMC/sv-benchmarks/c/ldv-memsafety/memleaks_test22_3-1.yml')
		dlg = DlgYaml(self)
		dlg.showYaml(fuSeBMCYAMLParser)
		
		button = dlg.exec_()
		if button == QDialog.DialogCode.Accepted:
			yamlDict = dlg.getSelectedData()
			self.txtBenchmark.setText(yamlDict.get('input_file', ''))
			#self.cmbProperty.setCurrentText(yamlDict.get('property', ''))
			self.SetSelectedCategory(yamlDict.get('category_property', None))
			self.cmbArch.setCurrentText(yamlDict.get('arch', ''))
	def btnGenerateCmd_clicked(self):
		self.GenerateCommandAndXMLParams()
		self.txtXMLParams.setPlainText(self.strXMLParams)
		self.lstCommand.extend(self.lstSpecific)
		self.lstCommand.append(self.txtBenchmark.text())
		cmd_line = ' '.join(self.lstCommand)
		self.txtCommand.setPlainText('./fusebmc.py ' + cmd_line)

	def chkECHandleInfiniteWhileLoopToggled(self):
		fuzz1 = self.chkErrorCallFuzzer1.isChecked()
		self.spnECInfiniteWhileLoopIncrementTime.setEnabled(fuzz1 and self.chkECHandleInfiniteWhileLoop.isChecked())
	
	def chkCBHandleInfiniteWhileLoopToggled(self):
		fuzz1 = self.chkCoverBrancherFuzzer1.isChecked()
		self.spnCBInfiniteWhileLoopIncrementTime.setEnabled(fuzz1 and self.chkCBHandleInfiniteWhileLoop.isChecked())
	def chkCBHandleSelectiveInputToggled(self):
		fuzz1 = self.chkCoverBrancherFuzzer1.isChecked()
		self.spnCBSelectiveInputIncrementTime.setEnabled(fuzz1 and self.chkCBHandleSelectiveInput.isChecked())
	
	def chkECHandleSelectiveInputToggled(self):
		fuzz1 = self.chkErrorCallFuzzer1.isChecked()
		self.spnECSelectiveInputIncrementTime.setEnabled(fuzz1 and self.chkECHandleSelectiveInput.isChecked())
	def chkCBUnlimitedKStepToggled(self):
		unlimitedK = self.chkCBUnlimitedKStep.isChecked()
		self.spnCBMaxKStep.setEnabled(not unlimitedK)
		self.lblCBMaxKStep.setEnabled(not unlimitedK)
	def chkECUnlimitedKStepToggled(self):
		unlimitedK = self.chkECUnlimitedKStep.isChecked()
		self.spnECMaxKStep.setEnabled(not unlimitedK)
		self.lblECMaxKStep.setEnabled(not unlimitedK)
	def chkTUnlimitedKStepToggled(self):
		unlimitedK = self.chkTUnlimitedKStep.isChecked()
		self.spnTMaxKStep.setEnabled(not unlimitedK)
		self.lblTMaxKStep.setEnabled(not unlimitedK)
	
	'''def chkTUnlimitedContextBoundToggled(self):
		unlimitedC = self.chkTUnlimitedContextBound.isChecked()
		self.spnTMaxContextBound.setEnabled(not unlimitedC)
		self.lblTMaxContextBound.setEnabled(not unlimitedC)
	'''
	def chkCoverBrancherFuzzer1Toggled(self):
		fuzz1 = self.chkCoverBrancherFuzzer1.isChecked()
		self.spnCoverBranchesFuzzer1Time.setEnabled(fuzz1)
		self.chkCoverBrancherFuzzer2.setEnabled(fuzz1)
		
		self.spnCoverBranchesFuzzer2Time.setEnabled(fuzz1 and self.chkCoverBrancherFuzzer2.isChecked())
		self.spnCoverBranchesMinNumOfTCRunAFL.setEnabled(fuzz1)
		
		self.chkCBHandleInfiniteWhileLoop.setEnabled(fuzz1)
		self.spnCBInfiniteWhileLoopIncrementTime.setEnabled(fuzz1 and self.chkCBHandleInfiniteWhileLoop.isChecked())
		
		self.chkCBHandleSelectiveInput.setEnabled(fuzz1)
		self.spnCBSelectiveInputIncrementTime.setEnabled(fuzz1 and self.chkCBHandleSelectiveInput.isChecked())
		
		
	
	def chkCoverBrancherFuzzer2Toggled(self):
		self.spnCoverBranchesFuzzer2Time.setEnabled(self.chkCoverBrancherFuzzer1.isChecked() and self.chkCoverBrancherFuzzer2.isChecked())
		
	def chkErrorCallFuzzer1Toggled(self):
		fuzz1 = self.chkErrorCallFuzzer1.isChecked()
		self.spnErrorCallFuzzer1Time.setEnabled(fuzz1)
		self.chkErrorCallFuzzer2.setEnabled(fuzz1)
		
		self.spnErrorCallFuzzer2Time.setEnabled(fuzz1 and self.chkErrorCallFuzzer2.isChecked())
		self.spnECNumGeneratedSeeedsFuz1.setEnabled(fuzz1)
		#self.spnCoverBranchesMinNumOfTCRunAFL.setEnabled(fuzz1)
		self.chkECHandleInfiniteWhileLoop.setEnabled(fuzz1)
		self.spnECInfiniteWhileLoopIncrementTime.setEnabled(fuzz1 and self.chkECHandleInfiniteWhileLoop.isChecked())
		
		self.chkECHandleSelectiveInput.setEnabled(fuzz1)
		self.spnECSelectiveInputIncrementTime.setEnabled(fuzz1 and self.chkECHandleSelectiveInput.isChecked())

	def chkErrorCallFuzzer2Toggled(self):
		self.spnErrorCallFuzzer2Time.setEnabled(self.chkErrorCallFuzzer1.isChecked() and self.chkErrorCallFuzzer2.isChecked())
	def chkECRunESBMCTwiceToggled(self):
		runESBMCTwice = self.chkECRunESBMCTwice.isChecked()
		self.spnErrorCallESBMCRun1Time.setEnabled(runESBMCTwice)
	
	def cmbPropertyCurrentIndexChanged(self):
		#print(self.GetSelectedCategory())
		cat = self.GetSelectedCategory()
		self.tbParameters.setTabEnabled(0,False)
		for i in range(self.tbParameters.count()):
			self.tbParameters.setTabEnabled(i,False)
		
		if cat == Property.cover_branches:
			self.tbParameters.setTabEnabled(0, True)
			self.tbParameters.setCurrentIndex(0)
		elif cat == Property.cover_error_call:
			self.tbParameters.setTabEnabled(1, True)
			self.tbParameters.setCurrentIndex(1)
		elif cat == Property.termination or \
			cat == Property.unreach_call or \
			cat == Property.overflow or \
			cat == Property.memcleanup or \
			cat == Property.memsafety :
			
			self.tbParameters.setTabEnabled(2, True)
			self.tbParameters.setCurrentIndex(2)
		#print(dir(self.tbParameters))
	def cmbStrategyCurrentIndexChanged(self):
		isKInduction = self.cmbStrategy.currentIndex() == 1
		isFixed = self.cmbStrategy.currentIndex() == 3
		
		self.lblECMaxInductiveStep.setEnabled(isKInduction or isFixed)
		self.spnECMaxInductiveStep.setEnabled(isKInduction or isFixed)
		
		self.lblCBMaxInductiveStep.setEnabled(isKInduction or isFixed)
		self.spnCBMaxInductiveStep.setEnabled(isKInduction or isFixed)
		
		self.lblTMaxInductiveStep.setEnabled(isKInduction or isFixed)
		self.spnTMaxInductiveStep.setEnabled(isKInduction or isFixed)
		

	def cmbMLCurrentIndexChanged(self):
		idx = self.cmbML.currentIndex()
		self.cmbModel.setEnabled(idx == 2)
	
	def GetSelectedGoalSorting(self):
		return self.lstGoalSorting[self.cmbGoalSorting.currentIndex()]
	def GetSelectedCategory(self):
		return self.lstProperty[self.cmbProperty.currentIndex()]
	def SetSelectedCategory(self, cat):
		if cat is None : return
		idx = self.lstProperty.index(cat)
		if idx != -1:
			self.cmbProperty.setCurrentIndex(idx)

	def btnOpenResultDir_clicked(self):
		dir = str(QFileDialog.getExistingDirectory(self, "Result Directory"))
		self.txtResultDir.setText(dir)
		
	def btnOpenBenchmark_clicked(self):
		filename, _ = QFileDialog.getOpenFileName(self, 'Open file','', "Yaml files (*.yml);;Source files (*.i *.c);; All Files (*.*)")
		#print('filename:',filename,'tt:',type(filename))
		fName, ext = os.path.splitext(filename)
		if ext == '.yml':
			fuSeBMCYAMLParser = FuSeBMCYAMLParser()
			fuSeBMCYAMLParser.parse(filename)
			dlg = DlgYaml(self)
			dlg.showYaml(fuSeBMCYAMLParser)
			
			button = dlg.exec_()
			if button == QDialog.DialogCode.Accepted:
				yamlDict = dlg.getSelectedData()
				self.txtBenchmark.setText(yamlDict.get('input_file', ''))
				#self.cmbProperty.setCurrentText(yamlDict.get('property', ''))
				self.SetSelectedCategory(yamlDict.get('category_property', None))
				self.cmbArch.setCurrentText(yamlDict.get('arch', ''))
		elif isinstance(filename,str) and len(filename) > 0 and os.path.isfile(filename):
			self.txtBenchmark.setText(filename)
	def showErrMsg(self, msg:str)-> None:
		errDlg = QErrorMessage(self)
		errDlg.setWindowModality(Qt.WindowModal)
		errDlg.showMessage(msg)
		print('ERROR:', msg)
	
	def GenerateCommandAndXMLParams(self) -> None:
		"""
		This will fill (lstCommand, lstSpecific, lstXMLParams , strXMLParams)
		"""
		self.cat = self.GetSelectedCategory()
		tmpResultDir = self.txtResultDir.text().strip()
		hasResultDir = len(tmpResultDir) > 0
		isPredict = self.cmbML.currentIndex() == 2
		if isPredict:
			self.lstSpecific = []
		self.lstXMLParams = [
			('--strategy', self.cmbStrategy.currentText()) if not isPredict else (None,None),
			('--timeout', str(self.spnTimeout.value())),
			('--verbose',None) if self.chkVerbose.isChecked() else (None,None),
			('--ml', str(self.cmbML.currentIndex())),
			('--ml-model', str(self.cmbModel.currentIndex())) if isPredict else (None,None),
			#('--result-dir',tmpResultDir) if hasResultDir else (None,None)
						]
		self.lstCommand = [
							'-p', self.cmbProperty.currentText(),
							
							'-s' if not isPredict else '',
							self.cmbStrategy.currentText() if not isPredict else '',
							
							'--arch',self.cmbArch.currentText(),
							'--run-testcov' if self.chkRunTestCov.isChecked() else '',
							'--result-dir' if hasResultDir else '', tmpResultDir if hasResultDir else '',
							'--timeout', str(self.spnTimeout.value()),
							'--verbose' if self.chkVerbose.isChecked() else '',
							'--ml', str(self.cmbML.currentIndex()),
							
							'--ml-model' if isPredict else '',
							str(self.cmbModel.currentIndex()) if isPredict else '',
							
							]
		
		self.lstSpecific = []
		isKInduction = self.cmbStrategy.currentIndex() == 1
		isFixed = self.cmbStrategy.currentIndex() == 3
		
		if self.cat == Property.cover_branches:
			fuzz1 = self.chkCoverBrancherFuzzer1.isChecked()
			fuzz2 = self.chkCoverBrancherFuzzer2.isChecked()
			fuzz1ANDfuzz2 = fuzz1 and fuzz2
			coverBranchesHandleInfiniteWhileLoop = self.chkCBHandleInfiniteWhileLoop.isChecked()
			coverBranchesHandleSelectiveInputs= self.chkCBHandleSelectiveInput.isChecked()
			if not isPredict:
				self.lstSpecific = [
						'--fuzzer-cover-branches-1' if fuzz1 else '',
						'--fuzzer-cover-branches-1-time' if fuzz1 else '',
						str(self.spnCoverBranchesFuzzer1Time.value()) if fuzz1 else '',
						
						'--fuzzer-cover-branches-2' if fuzz1ANDfuzz2 else '',
						'--fuzzer-cover-branches-2-time' if fuzz1ANDfuzz2 else '',
						str(self.spnCoverBranchesFuzzer2Time.value()) if fuzz1ANDfuzz2 else '',
						'--goal-tracer' if self.chkGoalTracer.isChecked() else '',
						'--goal-sorting', str(self.GetSelectedGoalSorting()),
						'--global-depth' if self.chkGlobalDepth.isChecked() else '',
						'--cover-branches-num-testcases-to-run-afl' if fuzz1 else '',
						str(self.spnCoverBranchesMinNumOfTCRunAFL.value()) if fuzz1 else '',
						
						'--handle-infinite-while-loop-cover-branches' if fuzz1 and coverBranchesHandleInfiniteWhileLoop else '',
						'--cover-branches-infinite-while-loop-increment-time' if fuzz1 and coverBranchesHandleInfiniteWhileLoop else '',
						str(self.spnCBInfiniteWhileLoopIncrementTime.value()) if fuzz1 and coverBranchesHandleInfiniteWhileLoop else '',
						
						'--cover-branches-selective-inputs-enable' if fuzz1 and coverBranchesHandleSelectiveInputs else '',
						'--cover-branches-selective-inputs-increment-time' if fuzz1 and coverBranchesHandleSelectiveInputs else '',
						str(self.spnCBSelectiveInputIncrementTime.value()) if fuzz1 and coverBranchesHandleSelectiveInputs else '',
						
						'--max-k-step',
						'-1' if self.chkCBUnlimitedKStep.isChecked() else str(self.spnCBMaxKStep.value()),
						
						'--unwind' , str(self.spnCBUnwind.value()),
						'--k-step' , str(self.spnCBKStep.value()),
						'--context-bound' , str(self.spnCBContextBound.value()),
						
						'--max-inductive-step' if isKInduction or isFixed else '',
						str(self.spnCBMaxInductiveStep.value()) if isKInduction or isFixed else '',
						
							]
		elif self.cat == Property.cover_error_call:
			fuzz1 = self.chkErrorCallFuzzer1.isChecked()
			fuzz2 = self.chkErrorCallFuzzer2.isChecked()
			fuzz1ANDfuzz2 = fuzz1 and fuzz2
			runESBMCTwice = self.chkECRunESBMCTwice.isChecked()
			errorCallHandleInfiniteWhileLoop = self.chkECHandleInfiniteWhileLoop.isChecked()
			errorCallHandleSelectiveInputs= self.chkECHandleSelectiveInput.isChecked()
			if not isPredict:
				self.lstSpecific = [
						'--fuzzer-error-call-1' if fuzz1 else '',
						'--fuzzer-error-call-1-time' if fuzz1 else '',
						str(self.spnErrorCallFuzzer1Time.value()) if fuzz1 else '',
						'--fuzzer-error-call-2' if fuzz1ANDfuzz2 else '',
						
						'--fuzzer-error-call-2-time' if fuzz1ANDfuzz2 else '',
						str(self.spnErrorCallFuzzer2Time.value()) if fuzz1ANDfuzz2 else '',
						
						'--run-esbmc-twice-error-call' if runESBMCTwice else '',
						'--esbmc-error-call-run-1-time' if runESBMCTwice else '',
						str(self.spnErrorCallESBMCRun1Time.value()) if runESBMCTwice else '',
						
						'--seeds-num-fuzzer1-error-call' if fuzz1 else '',
						str(self.spnECNumGeneratedSeeedsFuz1.value()) if fuzz1 else '',
						'--handle-infinite-while-loop-error-call' if fuzz1 and errorCallHandleInfiniteWhileLoop else '',
						
						'--error-call-infinite-while-loop-increment-time' if fuzz1 and errorCallHandleInfiniteWhileLoop else '',
						str(self.spnECInfiniteWhileLoopIncrementTime.value()) if fuzz1 and errorCallHandleInfiniteWhileLoop else '',
						
						'--error-call-selective-inputs-enable' if fuzz1 and errorCallHandleSelectiveInputs else '',
						'--error-call-selective-inputs-increment-time' if fuzz1 and errorCallHandleSelectiveInputs else '',
						str(self.spnECSelectiveInputIncrementTime.value()) if fuzz1 and errorCallHandleSelectiveInputs else '',
						
						'--max-k-step',
						'-1' if self.chkECUnlimitedKStep.isChecked() else str(self.spnECMaxKStep.value()),
						'--k-step' , str(self.spnECKStep.value()),
						'--context-bound' , str(self.spnECContextBound.value()),
						
						'--max-inductive-step' if isKInduction or isFixed else '',
						str(self.spnECMaxInductiveStep.value()) if isKInduction or isFixed else '',
						
					]
		elif self.cat == Property.termination or \
			self.cat == Property.unreach_call or \
			self.cat == Property.overflow or \
			self.cat == Property.memcleanup or \
			self.cat == Property.memsafety :
			
			if not isPredict:
				self.lstSpecific = [
					'--max-k-step',
					'-1' if self.chkTUnlimitedKStep.isChecked() else str(self.spnTMaxKStep.value()),
					'--k-step' , str(self.spnTKStep.value()),
					
					'--context-bound' , str(self.spnTContextBound.value()),
					#'--max-context-bound', '-1' if self.chkTUnlimitedContextBound.isChecked() else str(self.spnTMaxContextBound.value()),
					#'--context-bound-step', str(self.spnTContextBoundStep.value()),
					
					'--max-inductive-step' if isKInduction or isFixed else '',
					str(self.spnTMaxInductiveStep.value()) if isKInduction or isFixed else '',
					'--unwind' , str(self.spnTUnwind.value()),
					'--add-symex-value-sets' if self.chkTAddSymexValueSets.isChecked() else '',
					
					]
		else:
			self.showErrMsg('Unsupported property:' + str(self.cat))
			return
		k , v = None, None
		
		for param in self.lstSpecific:
			if len(param) == 0: continue
			if param.startswith('--'):
				if k is None: pass
				else:
					self.lstXMLParams.append((k, v))
				k = param
			else:
				v = param
			if k is not None and v is not None:
				self.lstXMLParams.append((k, v))
				k , v = None, None
		if k is not None:self.lstXMLParams.append((k, v))
		self.strXMLParams = ''
		for (k,v) in self.lstXMLParams:
			if k is None:continue
			if v is not None:
				self.strXMLParams += '    <option name="'+k+'">'+v+'</option>\n'
			else:
				self.strXMLParams += '    <option name="'+k+'"/>\n'
		#return (lstCommand, lstSpecific, lstXMLParams , strXMLParams)

	def btnExec_clicked(self):
			
		#try:
			self.lblParametersGenerated.setVisible(False)
			#FuSeBMCParams.is_ctrl_c = False
			#FuSeBMCParams.benchmark = '../../sv-benchmarks/c/eca-rers2012/Problem12_label00.c'
			
			#FuSeBMCParams.benchmark = 'sv-benchmarks/c/seq-mthreaded/pals_lcr.4.ufo.BOUNDED-8.pals.c'
			#FuSeBMCParams.propertyFile = '../../sv-benchmarks/c/properties/coverage-branches.prp'
			#FuSeBMCParams.arch = '64'
			#FuSeBMCParams.strategy = 'incr'
			
			self.btnExec.setEnabled(False)
			self.btnStop.setEnabled(True)
		
			###
			#cmd_line = ' '.join(['ls', '-l'])
			self.GenerateCommandAndXMLParams()
			#print('lstXMLParams',lstXMLParams)
			
			self.txtXMLParams.setPlainText(self.strXMLParams)
			
			self.lstCommand.extend(self.lstSpecific)
			self.lstCommand.append(self.txtBenchmark.text())
			cmd_line = ' '.join(self.lstCommand)
			the_args = shlex.split(cmd_line)
			print(the_args)
			self.txtCommand.setPlainText('./fusebmc.py ' + cmd_line)
			self.tblCoverBranchesResult.setRowCount(0)
			self.worker = Worker(self, the_args)
			self.thread = QThread()
		
			####
			
			self.worker.moveToThread(self.thread)
			self.worker.finished.connect(self.OnWorkerFinished)
			self.worker.dataFromFuSeBMCReady.connect(self.OnDataFromFuSeBMCReady)
			self.thread.started.connect(self.worker.procCounter)
			self.thread.start()
			
			'''
			FuSeBMCParams.benchmark = '../../sv-benchmarks/c/eca-rers2012/Problem12_label00.c'
			
			FuSeBMCParams.benchmark = 'sv-benchmarks/c/seq-mthreaded/pals_lcr.4.ufo.BOUNDED-8.pals.c'
			FuSeBMCParams.propertyFile = '../../sv-benchmarks/c/properties/coverage-branches.prp'
			FuSeBMCParams.arch = '64'
			FuSeBMCParams.strategy = 'incr'
			
			RunFuSeBMC();
			QMessageBox.information(self, "Info", "Connected....")
			'''
			pass
		#except:
		#	 QMessageBox.critical(self, "Error", "Connection Error")
	def OnDataFromFuSeBMCReady(self, data: str):
		#print('We have data', data)
		try:
			#rootXML = ET.parse(data).getroot()
			elem = ET.fromstring(data)
			if elem is not None:
				if elem.tag == 'outputdir': self.txtRunOutputDir.setText(elem.text)
				elif elem.tag == 'mlparams':
					self.showMLParams(elem)

			
			#print(elem)
		except Exception as ex:
			print(ex)

	def showMLParams(self, elem:ET.Element):
		self.lblParametersGenerated.setVisible(True)
		lProp = int(elem.find('prop').text)
		lstrategy = int(elem.find('strategy').text)
		lIsClassification= bool(int(elem.find('isClassification').text))
		lBestScoreClass = float(elem.find('bestScoreClass').text)
		self.cmbStrategy.setCurrentIndex(lstrategy)
		if lProp == Property.cover_error_call or lProp == Property.cover_branches:
			lk_step = int(elem.find('k_step').text)
			lMAX_K_STEP = int(elem.find('MAX_K_STEP').text)
			lcontextBound = int(elem.find('contextBound').text)
			lmaxInductiveStep = int(elem.find('maxInductiveStep').text)
			lfuzz1Enabled = bool(int(elem.find('fuzz1Enabled').text))
			lfuzz1time = int(elem.find('fuzz1time').text)
			lseedsNum = int(elem.find('seedsNum').text)
			lfuzz2Enabled = bool(int(elem.find('fuzz2Enabled').text))
			lfuzz2time = int(elem.find('fuzz2time').text)
			lwhileLoopEnabled = bool(int(elem.find('whileLoopEnabled').text))
			lwhileLoopTime = int(elem.find('whileLoopTime').text)
			lselectiveInputEnabled = bool(int(elem.find('selectiveInputEnabled').text))
			lselectiveInputTime = int(elem.find('selectiveInputTime').text)
			
			if lProp == Property.cover_error_call:
				lruntwice = bool(int(elem.find('runtwice').text))
				lesbmcRun1time = int(elem.find('esbmcRun1time').text)
				self.spnECKStep.setValue(lk_step)
				if lMAX_K_STEP != -1 :
					self.spnECMaxKStep.setValue(lMAX_K_STEP)
				self.chkECUnlimitedKStep.setChecked(lMAX_K_STEP == -1)
				self.spnECContextBound.setValue(lcontextBound)
				self.spnECMaxInductiveStep.setValue(lmaxInductiveStep)
				self.chkErrorCallFuzzer1.setChecked(lfuzz1Enabled)
				self.spnErrorCallFuzzer1Time.setValue(lfuzz1time)
				self.spnECNumGeneratedSeeedsFuz1.setValue(lseedsNum)
				self.chkErrorCallFuzzer2.setChecked(lfuzz2Enabled)
				self.spnErrorCallFuzzer2Time.setValue(lfuzz2time)
				self.chkECRunESBMCTwice.setChecked(lruntwice)
				self.spnErrorCallESBMCRun1Time.setValue(lesbmcRun1time)
				self.chkECHandleInfiniteWhileLoop.setChecked(lwhileLoopEnabled)
				self.spnECInfiniteWhileLoopIncrementTime.setValue(lwhileLoopTime)
				self.chkECHandleSelectiveInput.setChecked(lselectiveInputEnabled)
				self.spnECSelectiveInputIncrementTime.setValue(lselectiveInputTime)
			
			if lProp == Property.cover_branches:
				lunwind= int(elem.find('unwind').text)
				lgoalTracer = int(elem.find('goalTracer').text)
				lglobalDepth = bool(int(elem.find('globalDepth').text))
				lgoalSorting = int(elem.find('goalSorting').text)
				self.spnCBKStep.setValue(lk_step)
				if lMAX_K_STEP != -1 :
					self.spnCBMaxKStep.setValue(lMAX_K_STEP)
				self.chkCBUnlimitedKStep.setChecked(lMAX_K_STEP == -1)
				self.spnCBContextBound.setValue(lcontextBound)
				self.spnCBMaxInductiveStep.setValue(lmaxInductiveStep)
				self.chkCoverBrancherFuzzer1.setChecked(lfuzz1Enabled)
				self.spnCoverBranchesFuzzer1Time.setValue(lfuzz1time)
				
				self.spnCoverBranchesMinNumOfTCRunAFL.setValue(lseedsNum)
				self.chkCoverBrancherFuzzer2.setChecked(lfuzz2Enabled)
				self.spnCoverBranchesFuzzer2Time.setValue(lfuzz2time)
				#self.chkECRunESBMCTwice.setChecked(lruntwice)
				#self.spnErrorCallESBMCRun1Time.setValue(lesbmcRun1time)
				self.chkCBHandleInfiniteWhileLoop.setChecked(lwhileLoopEnabled)
				self.spnCBInfiniteWhileLoopIncrementTime.setValue(lwhileLoopTime)
				self.chkCBHandleSelectiveInput.setChecked(lselectiveInputEnabled)
				self.spnCBSelectiveInputIncrementTime.setValue(lselectiveInputTime)
				self.spnCBUnwind.setValue(lunwind)
				self.chkGoalTracer.setChecked(lgoalTracer)
				self.chkGlobalDepth.setChecked(lglobalDepth)
				self.cmbGoalSorting.setCurrentIndex(self.lstGoalSorting.index(lgoalSorting))
		elif lProp == Property.unreach_call or \
			 lProp == Property.overflow or \
			 lProp == Property.termination or \
			 lProp == Property.memcleanup or \
			 lProp == Property.memsafety :
			
			lk_step = int(elem.find('k_step').text)
			lMAX_K_STEP = int(elem.find('MAX_K_STEP').text)
			lcontextBound = int(elem.find('contextBound').text)
			lmaxInductiveStep = int(elem.find('maxInductiveStep').text)
			#lcontextBoundStep = int(elem.find('contextBoundStep').text)
			#lmaxContextBound = int(elem.find('maxContextBound').text)
			lUNWIND = int(elem.find('UNWIND').text)
			lAddSymexValueSets = int(elem.find('addSymexValueSets').text)
			
			self.chkTUnlimitedKStep.setChecked(lMAX_K_STEP == -1)
			self.spnTMaxKStep.setValue(lMAX_K_STEP)
			self.spnTKStep.setValue(lk_step)
			#self.chkTUnlimitedContextBound.setChecked(lmaxContextBound == -1)
			#self.spnTMaxContextBound.setValue(lmaxContextBound)
			#self.spnTContextBoundStep.setValue(lcontextBoundStep)
			self.spnTContextBound.setValue(lcontextBound)
			self.spnTMaxInductiveStep.setValue(lmaxInductiveStep)
			self.spnTUnwind.setValue(lUNWIND)
			self.chkTAddSymexValueSets.setChecked(lAddSymexValueSets == 1)
		else:
			self.showErrMsg(f"Property {lProp} is not supported in function 'showMLParams' !!")
			
			
		
		
		paramsGenStr = 'Classification: ' if lIsClassification else 'Regression: '
		paramsGenStr += str(lBestScoreClass)
		self.lblParametersGenerated.setText(paramsGenStr)
			
	
	def showCoverBranchesJson(self, jsonFile:str):
		self.tblCoverBranchesResult.setRowCount(0)
		
		with open(jsonFile, 'r') as f:
			jsn_data = json.load(f)
			if isinstance(jsn_data, list):
				self.tblCoverBranchesResult.setRowCount(len(jsn_data))
				row = 0
				for tc_dict in jsn_data:
					self.tblCoverBranchesResult.setItem(row, 0, QTableWidgetItem(tc_dict.get('Test','')))
					self.tblCoverBranchesResult.setItem(row, 1, QTableWidgetItem(str(tc_dict.get('Coverage (individual)',''))))
					self.tblCoverBranchesResult.setItem(row, 2, QTableWidgetItem(str(tc_dict.get('Coverage (accumulated)',''))))
					self.tblCoverBranchesResult.setItem(row, 3, QTableWidgetItem(str(tc_dict.get('Part of reduced suite',''))))
					row += 1
			self.tblCoverBranchesResult.resizeColumnsToContents()
			self.tblCoverBranchesResult.resizeRowsToContents()

	def OnWorkerFinished(self):
		jsonFile = self.txtRunOutputDir.text() + '/output_cov/results.json'
		if os.path.isfile(jsonFile):
			self.showCoverBranchesJson(jsonFile)
		self.thread.quit()
		self.btnExec.setEnabled(True)
		self.btnStop.setEnabled(False)

	def btnStop_clicked(self):
		#FuSeBMCParams.is_ctrl_c = True
		
		#FuSeBMCParams.forceStop = True
		#self.thread.terminate()
		#self.thread.quit()
		#self.thread.wait()
		self.worker.SendTermSignal()
		'''if self.thread.isRunning():
			self.thread.terminate()
			self.thread.wait()
		self.btnExec.setEnabled(True)
		self.btnStop.setEnabled(False)
'''

app = QApplication(sys.argv)
mainWindow = FuSeBMCMainWindow()
mainWindow.show()

sys.exit(app.exec_())