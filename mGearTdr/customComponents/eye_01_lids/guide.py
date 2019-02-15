"""Guide Eye 01 module"""

from functools import partial
from mgear.shifter.component import guide
from mgear.core import transform, pyqt
from mgear.vendor.Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget

import settingsUI as sui


# guide info
AUTHOR = "Jeremie Passerin, Miquel Campos, Duncan Rudd"
URL = "www.jeremiepasserin.com, www.miquletd.com, www.3drstudio.co.uk"
EMAIL = "geerem@hotmail.com, hello@miquel-campos.com, hello@3drstudio.co.uk"
VERSION = [0, 0, 1]
TYPE = "eye_01_lids"
NAME = "eye"
DESCRIPTION = "eye control rig with 3 joint lids and fat layer"

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

    def postInit(self):
        """Initialize the position for the guide"""
        self.save_transform = ["root", "look", 'lids',
                               'topLid1', 'topLid2', 'topLid3',
                               'btmLid1', 'btmLid2', 'btmLid3']

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        # eye guide
        self.root = self.addRoot()
        vTemp = transform.getOffsetPosition(self.root, [0, 0, 1])
        self.look = self.addLoc("look", self.root, vTemp)

        vTemp = transform.getOffsetPosition(self.root, [0, 0, 0])
        self.lids = self.addLoc('lids', self.root, vTemp)
        self.lids.s.set(.5, .5, .5)

        vTemp = transform.getOffsetPosition(self.lids, [-.1, .025, .25])
        self.topLid1 = self.addLoc('topLid1', self.lids, vTemp)
        self.topLid1.s.set(.2, .2, .2)

        vTemp = transform.getOffsetPosition(self.lids, [0, .025, .25])
        self.topLid2 = self.addLoc('topLid2', self.lids, vTemp)
        self.topLid2.s.set(.2, .2, .2)

        vTemp = transform.getOffsetPosition(self.lids, [.1, .025, .25])
        self.topLid3 = self.addLoc('topLid3', self.lids, vTemp)
        self.topLid3.s.set(.2, .2, .2)

        vTemp = transform.getOffsetPosition(self.lids, [-.1, -.025, .25])
        self.btmLid1 = self.addLoc('btmLid1', self.lids, vTemp)
        self.btmLid1.s.set(.2, .2, .2)

        vTemp = transform.getOffsetPosition(self.lids, [0, -.025, .25])
        self.btmLid2 = self.addLoc('btmLid2', self.lids, vTemp)
        self.btmLid2.s.set(.2, .2, .2)

        vTemp = transform.getOffsetPosition(self.lids, [.1, -.025, .25])
        self.btmLid3 = self.addLoc('btmLid3', self.lids, vTemp)
        self.btmLid3.s.set(.2, .2, .2)

        centers = [self.root, self.look]
        self.dispcrv = self.addDispCurve("crv", centers)

    def addParameters(self):
        """Add the configurations settings"""

        self.pUpVDir = self.addEnumParam(
            "upVectorDirection", ["X", "Y", "Z"], 1)

        self.pIkRefArray = self.addParam("ikrefarray", "string", "")
        self.pUseIndex = self.addParam("useIndex", "bool", False)

        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)


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
        self.resize(280, 350)

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
        self.settingsTab.upVectorDirection_comboBox.setCurrentIndex(
            self.root.attr("upVectorDirection").get())

        ikRefArrayItems = self.root.attr("ikrefarray").get().split(",")
        for item in ikRefArrayItems:
            self.settingsTab.ikRefArray_listWidget.addItem(item)

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        cBox = self.settingsTab.upVectorDirection_comboBox
        cBox.currentIndexChanged.connect(
            partial(self.updateComboBox,
                    self.settingsTab.upVectorDirection_comboBox,
                    "upVectorDirection"))

        self.settingsTab.ikRefArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))

        self.settingsTab.ikRefArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))

        self.settingsTab.ikRefArray_listWidget.installEventFilter(self)

    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.ikRefArray_listWidget:
                self.updateListAttr(sender, "ikrefarray")
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)