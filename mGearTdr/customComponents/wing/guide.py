"""Guide Wing module"""

from functools import partial
import pymel.core as pm
from mgear.shifter.component import guide
from mgear.core import transform, pyqt
from mgear.vendor.Qt import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget
import settingsUI as sui

# guide info
AUTHOR = "Jeremie Passerin, Miquel Campos, Duncan Rudd"
URL = "www.jeremiepasserin.com, www.miquel-campos.com, www.3drstudio.co.uk"
EMAIL = "geerem@hotmail.com, hello@miquel-campos.com, hello@3drstudio.co.uk"
VERSION = [0, 0, 1]
TYPE = "wing"
NAME = "wing"
DESCRIPTION = "2 bones arm with Maya nodes for roll bones. With elbow Pin.\n" \
              "Wing is driven by lofted nurbs surface.\n" \
              "Feathers are constrained to surface using spline IK chains driven by pointOnSurfaceInfo nodes"


##########################################################
# CLASS
##########################################################


class Guide(guide.ComponentGuide):
    """Component Guide Class"""

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    connectors = ["shoulder_01"]

    def postInit(self):
        """Initialize the position for the guide"""

        self.save_transform = ["root", "elbow", "wrist", "eff",
                               "finger0Start", "finger0Mid", "finger0End",
                               "finger1Start", "finger1Mid", "finger1End",
                               "finger2Start", "finger2Mid", "finger2End",
                               "finger3Start", "finger3Mid", "finger3End",
                               "finger4Start", "finger4Mid", "finger4End"]

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        self.root = self.addRoot()

        vTemp = transform.getOffsetPosition(self.root, [3, 0, -.01])
        self.elbow = self.addLoc("elbow", self.root, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [6, 0, 0])
        self.wrist = self.addLoc("wrist", self.elbow, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [7, 0, 0])
        self.eff = self.addLoc("eff", self.wrist, vTemp)

        self.dispcrv = self.addDispCurve(
            "crv",
            [self.root, self.elbow, self.wrist, self.eff])

        # ----------------EXTRA GUIDE BITS-----------------
        # finger0
        self.finger0Start = self.addLoc("finger0Start", self.root, (0, 0, 0))

        vTemp = transform.getOffsetPosition(self.finger0Start, [0, -2, 0])
        self.finger0Mid = self.addLoc("finger0Mid", self.finger0Start, vTemp)

        vTemp = transform.getOffsetPosition(self.finger0Start, [0, -4, 0])
        self.finger0End = self.addLoc("finger0End", self.finger0Start, vTemp)

        # finger1
        vTemp = transform.getOffsetPosition(self.elbow, [0, 0, 0])
        self.finger1Start = self.addLoc("finger1Start", self.elbow, vTemp)

        vTemp = transform.getOffsetPosition(self.finger1Start, [0, -2, 0])
        self.finger1Mid = self.addLoc("finger1Mid", self.finger1Start, vTemp)

        vTemp = transform.getOffsetPosition(self.finger1Start, [0, -4, 0])
        self.finger1End = self.addLoc("finger1End", self.finger1Start, vTemp)

        # finger2
        vTemp = transform.getOffsetPosition(self.wrist, [0, 0, 0])
        self.finger2Start = self.addLoc("finger2Start", self.wrist, vTemp)

        vTemp = transform.getOffsetPosition(self.finger2Start, [0, -2, 0])
        self.finger2Mid = self.addLoc("finger2Mid", self.finger2Start, vTemp)

        vTemp = transform.getOffsetPosition(self.finger2Start, [0, -4, 0])
        self.finger2End = self.addLoc("finger2End", self.finger2Start, vTemp)

        # finger3
        vWrist = pm.xform(self.wrist, q=1, t=1, ws=1)
        vEff = pm.xform(self.eff, q=1, t=1, ws=1)
        vAvg = [(vWrist[i] + vEff[i]) / 2.0 for i in range(3)]
        self.finger3Start = self.addLoc("finger3Start", self.wrist, vAvg)
        pm.parentConstraint(self.wrist, self.eff, self.finger3Start, mo=False)

        vTemp = transform.getOffsetPosition(self.finger3Start, [0, -2, 0])
        self.finger3Mid = self.addLoc("finger3Mid", self.finger3Start, vTemp)

        vTemp = transform.getOffsetPosition(self.finger3Start, [0, -4, 0])
        self.finger3End = self.addLoc("finger3End", self.finger3Start, vTemp)

        # finger4
        vTemp = transform.getOffsetPosition(self.eff, [0, 0, 0])
        self.finger4Start = self.addLoc("finger4Start", self.eff, vTemp)

        vTemp = transform.getOffsetPosition(self.finger4Start, [0, -2, 0])
        self.finger4Mid = self.addLoc("finger4Mid", self.finger4Start, vTemp)

        vTemp = transform.getOffsetPosition(self.finger4Start, [0, -4, 0])
        self.finger4End = self.addLoc("finger4End", self.finger4Start, vTemp)

    def addParameters(self):
        """Add the configurations settings"""

        # Default Values
        self.pBlend = self.addParam("blend", "double", 1, 0, 1)
        self.pIkRefArray = self.addParam("ikrefarray", "string", "")
        self.pUpvRefArray = self.addParam("upvrefarray", "string", "")
        self.pUpvRefArray = self.addParam("pinrefarray", "string", "")
        self.pMaxStretch = self.addParam("maxstretch", "double", 1.5, 1, None)
        self.pIKTR = self.addParam("ikTR", "bool", False)
        self.pSuptJnts = self.addParam("supportJoints", "bool", True)
        self.pMirrorMid = self.addParam("mirrorMid", "bool", False)
        self.pMirrorIK = self.addParam("mirrorIK", "bool", False)
        self.pExtraTweak = self.addParam("extraTweak", "bool", False)

        # Feather Values
        self.pPrimaries = self.addParam('numPrimaries', 'long', 8, 0, None)
        self.numPointsPrimary = self.addParam('numPointsPrimary', 'long', 5, 3, None)
        self.numJointsPrimary = self.addParam('numJointsPrimary', 'long', 4, 3, None)
        self.pEnablePCoverts = self.addParam('enablePCoverts', 'bool', True)
        self.pLengthPCoverts = self.addParam('lengthPCoverts', 'double', 0.5, 0, 1)
        self.numPointsPCoverts = self.addParam('numPointsPCoverts', 'long', 3, 2, None)
        self.numJointsPCoverts = self.addParam('numJointsPCoverts', 'long', 3, 2, None)

        self.pSecondaries = self.addParam('numSecondaries', 'long', 8, 0, None)
        self.numPointsSecondary = self.addParam('numPointsSecondary', 'long', 5, 3, None)
        self.numJointsSecondary = self.addParam('numJointsSecondary', 'long', 4, 3, None)
        self.pEnableSCoverts = self.addParam('enableSCoverts', 'bool', True)
        self.pLengthSCoverts = self.addParam('lengthSCoverts', 'double', 0.5, 0, 1)
        self.numPointsSCoverts = self.addParam('numPointsSCoverts', 'long', 3, 3, None)
        self.numJointsSCoverts = self.addParam('numJointsSCoverts', 'long', 3, 2, None)
        self.pEnableSMarginals = self.addParam('enableSMarginals', 'bool', True)
        self.pLengthSMarginals = self.addParam('lengthSMarginals', 'double', 0.5, 0, 1)
        self.numPointsSMarginals = self.addParam('numPointsSMarginals', 'long', 3, 3, None)
        self.numJointsSMarginals = self.addParam('numJointsSMarginals', 'long', 3, 2, None)

        # Divisions
        self.pDiv0 = self.addParam("div0", "long", 2, 0, None)
        self.pDiv1 = self.addParam("div1", "long", 2, 0, None)

        # FCurves
        self.pSt_profile = self.addFCurveParam("st_profile",
                                               [[0, 0], [.5, -.5], [1, 0]])
        self.pSq_profile = self.addFCurveParam("sq_profile",
                                               [[0, 0], [.5, .5], [1, 0]])

        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam("parentJointIndex",
                                               "long",
                                               -1,
                                               None,
                                               None)

    def get_divisions(self):
        """ Returns correct segments divisions """

        if (self.root.hasAttr("supportJoints")
            and self.root.supportJoints.get()):
            ej = 2
        else:
            ej = 0

        self.divisions = self.root.div0.get() + self.root.div1.get() + 3 + ej

        return self.divisions


##########################################################
# Setting Page
##########################################################

class settingsTab(QtWidgets.QDialog, sui.Ui_Form):
    """The Component settings UI"""

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)
        self.setupUi(self)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):
    """Create the component setting window"""

    def __init__(self, parent=None):
        self.toolName = TYPE
        # Delete old instances of the componet settings window.
        pyqt.deleteInstances(self, MayaQDockWidget)

        super(self.__class__, self).__init__(parent=parent)
        self.settingsTab = settingsTab()

        self.setup_componentSettingWindow()
        self.create_componentControls()
        self.populate_componentControls()
        self.create_componentLayout()
        self.create_componentConnections()

    def setup_componentSettingWindow(self):
        self.mayaMainWindow = pyqt.maya_main_window()

        self.setObjectName(self.toolName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(TYPE)
        self.resize(280, 780)

    def create_componentControls(self):
        return

    def populate_componentControls(self):
        """Populate Controls

        Populate the controls values from the custom attributes of the
        component.

        """
        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        # populate component settings
        self.settingsTab.ikfk_slider.setValue(
            int(self.root.attr("blend").get() * 100))
        self.settingsTab.ikfk_spinBox.setValue(
            int(self.root.attr("blend").get() * 100))
        self.settingsTab.maxStretch_spinBox.setValue(
            self.root.attr("maxstretch").get())
        self.populateCheck(self.settingsTab.ikTR_checkBox, "ikTR")
        self.populateCheck(self.settingsTab.supportJoints_checkBox,
                           "supportJoints")
        self.populateCheck(self.settingsTab.mirrorMid_checkBox, "mirrorMid")
        self.populateCheck(self.settingsTab.mirrorIK_checkBox, "mirrorIK")
        self.populateCheck(self.settingsTab.extraTweak_checkBox, "extraTweak")
        self.settingsTab.div0_spinBox.setValue(self.root.attr("div0").get())
        self.settingsTab.div1_spinBox.setValue(self.root.attr("div1").get())
        ikRefArrayItems = self.root.attr("ikrefarray").get().split(",")

        for item in ikRefArrayItems:
            self.settingsTab.ikRefArray_listWidget.addItem(item)

        upvRefArrayItems = self.root.attr("upvrefarray").get().split(",")
        for item in upvRefArrayItems:
            self.settingsTab.upvRefArray_listWidget.addItem(item)

        pinRefArrayItems = self.root.attr("pinrefarray").get().split(",")
        for item in pinRefArrayItems:
            self.settingsTab.pinRefArray_listWidget.addItem(item)

        # Feather settings
        self.settingsTab.primaries_spinBox.setValue(self.root.attr("numPrimaries").get())
        self.settingsTab.pPoints_spinBox.setValue(self.root.attr("numPointsPrimary").get())
        self.settingsTab.pJoints_spinBox.setValue(self.root.attr("numJointsPrimary").get())
        self.populateCheck(self.settingsTab.pCoverts_checkBox, "enablePCoverts")
        self.settingsTab.pCoverts_slider.setValue(
            int(self.root.attr("lengthPCoverts").get() * 100))
        self.settingsTab.pCoverts_spinBox.setValue(
            int(self.root.attr("lengthPCoverts").get() * 100))
        self.settingsTab.pCovertsPoints_spinBox.setValue(self.root.attr("numPointsPCoverts").get())
        self.settingsTab.pCovertsJoints_spinBox.setValue(self.root.attr("numJointsPCoverts").get())

        self.settingsTab.secondaries_spinBox.setValue(self.root.attr("numSecondaries").get())
        self.settingsTab.sPoints_spinBox.setValue(self.root.attr("numPointsSecondary").get())
        self.settingsTab.sJoints_spinBox.setValue(self.root.attr("numJointsSecondary").get())
        self.populateCheck(self.settingsTab.sCoverts_checkBox, "enableSCoverts")
        self.settingsTab.sCoverts_slider.setValue(
            int(self.root.attr("lengthSCoverts").get() * 100))
        self.settingsTab.sCoverts_spinBox.setValue(
            int(self.root.attr("lengthSCoverts").get() * 100))
        self.settingsTab.sCovertsPoints_spinBox.setValue(self.root.attr("numPointsSCoverts").get())
        self.settingsTab.sCovertsJoints_spinBox.setValue(self.root.attr("numJointsSCoverts").get())
        self.populateCheck(self.settingsTab.sMarginals_checkBox, "enableSMarginals")
        self.settingsTab.sMarginals_slider.setValue(
            int(self.root.attr("lengthSMarginals").get() * 100))
        self.settingsTab.sMarginals_spinBox.setValue(
            int(self.root.attr("lengthSMarginals").get() * 100))
        self.settingsTab.sMarginalsPoints_spinBox.setValue(self.root.attr("numPointsSMarginals").get())
        self.settingsTab.sMarginalsJoints_spinBox.setValue(self.root.attr("numJointsSMarginals").get())


        # populate connections in main settings
        self.c_box = self.mainSettingsTab.connector_comboBox
        for cnx in Guide.connectors:
            self.c_box.addItem(cnx)
        self.connector_items = [self.c_box.itemText(i) for i in
                                range(self.c_box.count())]

        currentConnector = self.root.attr("connector").get()
        if currentConnector not in self.connector_items:
            self.c_box.addItem(currentConnector)
            self.connector_items.append(currentConnector)
            pm.displayWarning(
                "The current connector: %s, is not a valid connector for this"
                " component. Build will Fail!!")
        comboIndex = self.connector_items.index(currentConnector)
        self.c_box.setCurrentIndex(comboIndex)

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.pCoverts_slider.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.pCoverts_slider, "lengthPCoverts"))

        self.settingsTab.pCoverts_spinBox.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.pCoverts_spinBox, "lengthPCoverts"))

        self.settingsTab.sCoverts_slider.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.sCoverts_slider, "lengthSCoverts"))

        self.settingsTab.sCoverts_spinBox.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.sCoverts_spinBox, "lengthSCoverts"))
        
        self.settingsTab.sMarginals_slider.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.sMarginals_slider, "lengthSMarginals"))

        self.settingsTab.sMarginals_spinBox.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.sMarginals_spinBox, "lengthSMarginals"))

        self.settingsTab.primaries_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.primaries_spinBox, "numPrimaries"))

        self.settingsTab.pPoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.pPoints_spinBox, "numPointsPrimary"))

        self.settingsTab.pJoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.pJoints_spinBox, "numJointsPrimary"))

        self.settingsTab.pCovertsPoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.pCovertsPoints_spinBox, "numPointsPCoverts"))

        self.settingsTab.pCovertsJoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.pCovertsJoints_spinBox, "numJointsPCoverts"))

        self.settingsTab.sCovertsPoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.sCovertsPoints_spinBox, "numPointsSCoverts"))

        self.settingsTab.sCovertsJoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.sCovertsJoints_spinBox, "numJointsSCoverts"))
        
        self.settingsTab.sMarginalsPoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.sMarginalsPoints_spinBox, "numPointsSMarginals"))

        self.settingsTab.sMarginalsJoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.sMarginalsJoints_spinBox, "numJointsSMarginals"))

        self.settingsTab.secondaries_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.secondaries_spinBox, "numSecondaries"))

        self.settingsTab.sPoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.sPoints_spinBox, "numPointsSecondary"))

        self.settingsTab.sJoints_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.sJoints_spinBox, "numJointsSecondary"))

        self.settingsTab.pCoverts_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.pCoverts_checkBox, "enablePCoverts"))

        self.settingsTab.sCoverts_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.sCoverts_checkBox, "enableSCoverts"))
        
        self.settingsTab.sMarginals_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.sMarginals_checkBox, "enableSMarginals"))

        self.settingsTab.ikfk_slider.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.ikfk_slider, "blend"))

        self.settingsTab.ikfk_spinBox.valueChanged.connect(
            partial(self.updateSlider, self.settingsTab.ikfk_spinBox, "blend"))

        self.settingsTab.maxStretch_spinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.maxStretch_spinBox, "maxstretch"))

        self.settingsTab.div0_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.div0_spinBox, "div0"))

        self.settingsTab.div1_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.div1_spinBox, "div1"))

        self.settingsTab.squashStretchProfile_pushButton.clicked.connect(
            self.setProfile)

        self.settingsTab.ikTR_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.ikTR_checkBox, "ikTR"))

        self.settingsTab.supportJoints_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.supportJoints_checkBox,
                    "supportJoints"))

        self.settingsTab.mirrorMid_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.mirrorMid_checkBox, "mirrorMid"))

        self.settingsTab.extraTweak_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.extraTweak_checkBox, "extraTweak"))

        self.settingsTab.mirrorIK_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.mirrorIK_checkBox,
                    "mirrorIK"))

        self.settingsTab.ikRefArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))

        self.settingsTab.ikRefArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))

        self.settingsTab.ikRefArray_copyRef_pushButton.clicked.connect(
            partial(self.copyFromListWidget,
                    self.settingsTab.upvRefArray_listWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))

        self.settingsTab.ikRefArray_listWidget.installEventFilter(self)

        self.settingsTab.upvRefArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.upvRefArray_listWidget,
                    "upvrefarray"))

        self.settingsTab.upvRefArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.upvRefArray_listWidget,
                    "upvrefarray"))

        self.settingsTab.upvRefArray_copyRef_pushButton.clicked.connect(
            partial(self.copyFromListWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    self.settingsTab.upvRefArray_listWidget,
                    "upvrefarray"))

        self.settingsTab.upvRefArray_listWidget.installEventFilter(self)

        self.settingsTab.pinRefArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.pinRefArray_listWidget,
                    "pinrefarray"))

        self.settingsTab.pinRefArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.pinRefArray_listWidget,
                    "pinrefarray"))

        self.settingsTab.pinRefArray_copyRef_pushButton.clicked.connect(
            partial(self.copyFromListWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    self.settingsTab.pinRefArray_listWidget,
                    "pinrefarray"))

        self.settingsTab.pinRefArray_listWidget.installEventFilter(self)

        self.mainSettingsTab.connector_comboBox.currentIndexChanged.connect(
            partial(self.updateConnector,
                    self.mainSettingsTab.connector_comboBox,
                    self.connector_items))

    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.ikRefArray_listWidget:
                self.updateListAttr(sender, "ikrefarray")
            elif sender == self.settingsTab.upvRefArray_listWidget:
                self.updateListAttr(sender, "upvrefarray")
            elif sender == self.settingsTab.pinRefArray_listWidget:
                self.updateListAttr(sender, "pinrefarray")
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
