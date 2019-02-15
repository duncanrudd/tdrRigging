"""Component Control 01 module"""

from mgear.shifter import component

from mgear.core import attribute, transform, primitive, node

import pymel.core as pm


#############################################
# COMPONENT
#############################################


def matrix44FromMtxAttr(initMtx):
    initMtx = initMtx.get()
    outList=[]
    def unpackList(outList, *args):
        for arg in args:
            if hasattr(arg, '__iter__'):
                unpackList(outList, *arg)
            else:
                outList.append(arg)
    unpackList(outList, *initMtx)
    mtxNode = pm.createNode('fourByFourMatrix')
    inputAttrs = ['in00', 'in01', 'in02', 'in03',
                  'in10', 'in11', 'in12', 'in13',
                  'in20', 'in21', 'in22', 'in23',
                  'in30', 'in31', 'in32', 'in33',]
    for source, dest in zip(outList, inputAttrs):
        print source, dest
        pm.Attribute('%s.%s' % (mtxNode.name(), dest)).set(source)
    return mtxNode




class CustomComponent(component.Main):
    """
    Custom component Class
    Inherits from Shifter base component
    Used to provide custom functionality to all custom components
    """
    def connect_blended_orient(self):
        if not self.parent == self.root.getParent():
            self.parent.addChild(self.root)

        refArray = self.settings["orientrefarray"]
        print 'function called: CustomComponent.connect_blended_orient()'

        if refArray:
            print 'ref array: %s' % refArray
            ref_names = self.get_valid_ref_list(refArray.split(","))
            if len(ref_names) == 1:
                print 'RELOADED'
                ref = self.rig.findRelative(ref_names[0])
                self.staticOffsetMtx = matrix44FromMtxAttr(
                    (ref.worldMatrix[0].get()*self.root.worldInverseMatrix[0].get()))
                self.targetMtx = node.createMultMatrixNode(ref.worldMatrix[0], self.root.worldInverseMatrix[0])
                self.targetInverseMtx = pm.createNode('inverseMatrix')
                self.targetMtx.matrixSum.connect(self.targetInverseMtx.inputMatrix)
                self.resultMtx = node.createMultMatrixNode(self.staticOffsetMtx.output,
                                                           self.targetInverseMtx.outputMatrix)

                dm = node.createDecomposeMatrixNode(self.resultMtx.matrixSum)
                pb = pm.createNode('pairBlend')
                dm.outputRotate.connect(pb.inRotate1)
                pb.rotInterpolation.set(1)
                pb.weight.set(0.5)
                pb.outRotateZ.connect(self.ik_cns.rotateZ)
                '''
                Do not use world space align in component settings - then control will be built oriented the same as the guide
                Align root to ik_cns.
                Then add above systems to ik_cns - this will offset away from original orientation of guide
                Add a buffer between ik_cns and control to maintain original orientation from guide. Align this buffer back to root
                '''
            else:
                pass

    def connect_blended_translate(self):
        if not self.parent == self.root.getParent():
            self.parent.addChild(self.root)

        refArray = self.settings["ikrefarray"]
        print 'function called: CustomComponent.connect_blended_translate()'

        if refArray:
            print 'ref array: %s' % refArray
            ref_names = self.get_valid_ref_list(refArray.split(","))
            ref = []
            for ref_name in ref_names:
                ref.append(self.rig.findRelative(ref_name))

            ref.append(self.ik_cns)
            cns_node = pm.pointConstraint(*ref, maintainOffset=False)
            cns_attr = pm.pointConstraint(
                cns_node, query=True, weightAliasList=True)

    def connect_blended_translate_and_orient(self):
        self.connect_blended_orient()
        self.connect_blended_translate()



