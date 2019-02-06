import pymel.core as pmc
import tdrRigging.utils.dagUtils as dagUtils

reload(dagUtils)

class TdrRig():
    def __init__(self, cleanup=1):
        self.buildNodes()

    def buildNodes(self):
        self.mainDag = pmc.group(empty=1, name='main_dag')
        self.rigDag = dagUtils.addChild(self.mainDag, 'group', name='rig_dag')
        self.geoDag = dagUtils.addChild(self.mainDag, 'group', name='geo_dag')
        self.configDag = dagUtils.addChild(self.mainDag, 'group', name='config_dag')

        pmc.addAttr(self.configDag, ln='geo_display', at='enum', enumName='normal:template:reference', hidden=0)
        self.geoDag.overrideEnabled.set(1)
        pmc.setAttr(self.configDag.geo_display, keyable=0)
        pmc.setAttr(self.configDag.geo_display, channelBox=1)
        self.configDag.geo_display.connect(self.geoDag.overrideDisplayType)

    def addCmpnt(self, cmpnt):
        cmpnt.mainDag.setParent(self.rigDag)