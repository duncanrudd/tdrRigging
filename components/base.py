import pymel.core as pmc
import tdrRigging.utils.dagUtils as dagUtils
import tdrRigging.utils.attributeUtils as attrUtils

reload(dagUtils)
reload(attrUtils)

class TdrBaseComponent(object):
    def __init__(self, name, side):
        self.name = name
        self.side = side
        self.ctrls = []

        # Create base hierarchy for component
        self.mainDag = pmc.group(empty=1, name='%s_cmpnt' % self.name)
        self.inputDag = dagUtils.addChild(self.mainDag, 'group', '%s_input' % self.name)
        self.controlsDag = dagUtils.addChild(self.mainDag, 'group', '%s_controls' % self.name)
        self.outputDag = dagUtils.addChild(self.mainDag, 'group', '%s_output' % self.name)
        self.rigDag = dagUtils.addChild(self.mainDag, 'group', '%s_rig' % self.name)
        self.deformDag = dagUtils.addChild(self.mainDag, 'group', '%s_deform' % self.name)

    def buildNodes(self):
        '''
        override this function in inheriting classes to build your components
        :return:
        '''
        pass
    def cleanUp(self):
        '''
        hides rig and deform groups. Override in child classes and call explicitly from within overriding function
        locks and hides visibility of controls and arnold attributes on shapes of controls
        :return:
        '''
        self.rigDag.visibility.set(0)
        self.deformDag.visibility.set(0)
        attrUtils.attrCtrl(nodeList=self.ctrls, attrList=['visibility'])

        # lock and hide arnold render attrs for control shapes
        for c in self.ctrls:
            shapes = pmc.listRelatives(c, s=1)
            for shape in shapes:
                attrList = ['aiRenderCurve', 'aiCurveWidth', 'aiSampleRate',
                            'aiCurveShaderR', 'aiCurveShaderG', 'aiCurveShaderB']
                for attr in attrList:
                    if not pmc.attributeQuery(attr, node=shape, ex=1):
                        attrList.remove(attr)
                attrUtils.attrCtrl(nodeList=[shape], attrList=attrList)