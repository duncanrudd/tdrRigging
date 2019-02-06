import pymel.core as pmc
import tdrRigging.utils.dagUtils as dagUtils
import tdrRigging.utils.attributeUtils as attrUtils
import base
import tdrRigging.objects.icons as icons

reload(dagUtils)
reload(attrUtils)
reload(base)
reload(icons)


class TdrRoot(base.TdrBaseComponent):
    def __init__(self, name, side, ctrlSize=20.0, cleanup=1):
        super(TdrRoot, self).__init__(name, side)
        self.ctrls = []
        self.buildNodes(ctrlSize)

    def buildNodes(self, ctrlSize):
        # controls

        self.root_01_ctrl = icons.hexIcon(name='root_01_ctrl', radius=ctrlSize)
        self.root_01_ctrl.setParent(self.controlsDag)
        self.ctrls.append(self.root_01_ctrl)

        self.root_02_ctrl = icons.hexIcon(name='root_02_ctrl', radius=ctrlSize*.85)
        self.root_02_ctrl.setParent(self.root_01_ctrl)
        self.ctrls.append(self.root_02_ctrl)

        self.root_03_ctrl = icons.hexIcon(name='root_03_ctrl', radius=ctrlSize*.7)
        self.root_03_ctrl.setParent(self.root_02_ctrl)
        self.ctrls.append(self.root_03_ctrl)

        dagUtils.colorize('green', self.ctrls)

    def assetize(self, publishCtrls=1):
        '''
        Adds all nodes associated with the component to a Maya asset container.
        :param: publishCtrls. If true. publishes the components controls so they are visible when asset is blackboxed
        :return: The newly created asset node
        '''
        nodes = pmc.ls('%s*' % self.name)
        self.asset = pmc.container(name='%s_asset' % self.name, addNode=nodes)
        pmc.container(self.asset, e=1, publishName='%s_%s' % (self.name, self.side))

        if publishCtrls:
            for ctrl in self.ctrls:
                pmc.containerPublish(self.asset, publishNode=[ctrl.name(), 'transform'], bindNode=[ctrl.name(), ctrl.name()])


    def cleanup(self):
        attrUtils.attrCtrl(nodeList=[self.root_02_ctrl, self.root_03_ctrl], attrList=['sx', 'sy', 'sz', 'visibility'])
        attrUtils.attrCtrl(nodeList=[self.root_01_ctrl], attrList=['visibility'])
        attrUtils.attrCtrl(nodeList=[self.root_01_ctrl], attrList=['sx', 'sy', 'sz'], lock=0)