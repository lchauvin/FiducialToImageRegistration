import os
import unittest
import tempfile
from __main__ import vtk, qt, ctk, slicer

#
# FiducialToImageRegistration
#

class FiducialToImageRegistration:
  def __init__(self, parent):
    parent.title = "Fiducial To Image Registration" # TODO make this more human readable by adding spaces
    parent.categories = ["Registration"]
    parent.dependencies = []
    parent.contributors = ["Laurent Chauvin (BWH), Junichi Tokuda (BWH)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module is automatically detecting spherical fiducial and register them to a set of points using an iterative closest point (ICP) registration method.
    """
    parent.acknowledgementText = """
    This file was originally developed by Laurent Chauvin, BWH and Junichi Tokuda, BWH  and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['FiducialToImageRegistration'] = self.runTest

  def runTest(self):
    tester = FiducialToImageRegistrationTest()
    tester.runTest()

#
# qFiducialToImageRegistrationWidget
#

class FiducialToImageRegistrationWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "FiducialToImageRegistration Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.volumeSelector = slicer.qMRMLNodeComboBox()
    self.volumeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.volumeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.volumeSelector.selectNodeUponCreation = True
    self.volumeSelector.addEnabled = False
    self.volumeSelector.removeEnabled = False
    self.volumeSelector.noneEnabled = False
    self.volumeSelector.showHidden = False
    self.volumeSelector.showChildNodeTypes = False
    self.volumeSelector.setMRMLScene( slicer.mrmlScene )
    self.volumeSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.volumeSelector)

    #
    # input fiducial list
    #
    self.fiducialSelector = slicer.qMRMLNodeComboBox()
    self.fiducialSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.fiducialSelector.selectNodeUponCreation = False
    self.fiducialSelector.addEnabled = False
    self.fiducialSelector.removeEnabled = False
    self.fiducialSelector.noneEnabled = False
    self.fiducialSelector.showHidden = False
    self.fiducialSelector.showChildNodeTypes = False
    self.fiducialSelector.setMRMLScene( slicer.mrmlScene )
    self.fiducialSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Fiducials: ", self.fiducialSelector)

    #
    # output transform selector
    #
    self.transformSelector = slicer.qMRMLNodeComboBox()
    self.transformSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.transformSelector.selectNodeUponCreation = True
    self.transformSelector.addEnabled = True
    self.transformSelector.removeEnabled = True
    self.transformSelector.renameEnabled = True
    self.transformSelector.noneEnabled = False
    self.transformSelector.showHidden = False
    self.transformSelector.showChildNodeTypes = False
    self.transformSelector.setMRMLScene( slicer.mrmlScene )
    self.transformSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Transform: ", self.transformSelector)

    #
    # registration error
    #
    self.registrationError = ctk.ctkDoubleSpinBox()
    self.registrationError.setToolTip("Registration Error")
    self.registrationError.minimum = 0
    self.registrationError.maximum = 1000
    parametersFormLayout.addRow("Registration Error: ", self.registrationError)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.fiducialSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.transformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.volumeSelector.currentNode() and self.transformSelector.currentNode() and self.fiducialSelector.currentNode()

  def onApplyButton(self):
    logic = FiducialToImageRegistrationLogic()
    print("Run the algorithm")
    logic.run(self.volumeSelector.currentNodeID, self.fiducialSelector.currentNodeID, self.transformSelector.currentNodeID, self.registrationError)

  def onReload(self,moduleName="FiducialToImageRegistration"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="FiducialToImageRegistration"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# FiducialToImageRegistrationLogic
#

class FiducialToImageRegistrationLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def delayDisplay(self,message,msec=1000):
    #
    # logic version of delay display
    #
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def run(self,iVolume,iFiducial,oTransform,registrationErrorWidget=None):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    # Get CLI modules
    fiducialDetectionCLI = slicer.modules.sphericalfiducialdetection
    icpRegistrationCLI = slicer.modules.icpregistration

    # Create temporary filename to store detected fiducials
    tmpFile = tempfile.NamedTemporaryFile()
    tmpFileName = tmpFile.name + ".fcsv"
    
    # Get nodes
    fiducialNode = slicer.mrmlScene.GetNodeByID(iFiducial)

    # Call fiducial detection
    detectionParameters = {}
    detectionParameters["inputVolume"] = iVolume
    detectionParameters["outputFile"] = tmpFileName
    detectionParameters["threshold"] = 0.0
    detectionParameters["numberOfSpheres"] = fiducialNode.GetNumberOfFiducials()
    detectionParameters["sigmaGrad"] = 1.0
    detectionParameters["gradThreshold"] = 0.1
    detectionParameters["minRadius"] = 5.0
    detectionParameters["maxRadius"] = 5.0
    detectionParameters["variance"] = 1.0
    detectionParameters["outputThreshold"] = 0.5
    detectionParameters["sphereRadiusRatio"] = 1.0

    detectionParameters["alpha"] = 0.8
    detectionParameters["beta"] = 0.8
    detectionParameters["gamma"] = 0.8

    detectionParameters["minSigma"] = 3.0
    detectionParameters["maxSigma"] = 3.0
    detectionParameters["stepSigma"] = 1.0
    
    detectionParameters["debugSwitch"] = 0
    
    slicer.cli.run(fiducialDetectionCLI, None, detectionParameters, True)

    # Import fiducials in slicer scene
    (success, detectedFiducialNode) = slicer.util.loadMarkupsFiducialList(tmpFileName, True)
    detectedFiducialNode.SetName(slicer.mrmlScene.GenerateUniqueName('SphericalFiducialsDetected'))

    # ICP Registration
    icpRegistrationError = 0.0
    registrationParameters = {}
    registrationParameters["movingPoints"] = iFiducial
    registrationParameters["fixedPoints"] = detectedFiducialNode.GetID()
    registrationParameters["registrationTransform"] = oTransform

    registrationParameters["iterations"] = 2000
    registrationParameters["gradientTolerance"] = 0.0001
    registrationParameters["valueTolerance"] = 0.0001
    registrationParameters["epsilonFunction"] = 0.00001

    cliNode = slicer.cli.run(icpRegistrationCLI, None, registrationParameters, True)

    if registrationErrorWidget:
      registrationErrorWidget.setValue(float(cliNode.GetParameterDefault(0,4)))

    print('Finished')

    return True


class FiducialToImageRegistrationTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_FiducialToImageRegistration1()

  def test_FiducialToImageRegistration1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = FiducialToImageRegistrationLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
