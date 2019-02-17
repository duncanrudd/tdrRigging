"""Component Eye 01 module"""

import pymel.core as pm
from pymel.core import datatypes

from mgear.shifter import component

from mgear.core import attribute, transform, primitive, applyop

import tdrRigging.utils.xformUtils as xformUtils
reload(xformUtils)

import tdrRigging.utils.mathUtils as mathUtils
reload(mathUtils)


##########################################################
# COMPONENT
##########################################################

# Specified whether the lids should travel with the rig or remain at the origin
# facilitating a blendshape workflow.
local = 1


class Component(component.Main):
    """Shifter component Class"""

    # =====================================================
    # OBJECTS
    # =====================================================
    def addObjects(self):
        """Add all the objects needed to create the component."""

        t = transform.getTransformFromPos(self.guide.pos["root"])

        self.eyeOver_npo = primitive.addTransform(
            self.root, self.getName("eyeOver_npo"), t)

        self.eyeOver_ctl = self.addCtl(self.eyeOver_npo,
                                       "Over_ctl",
                                       t,
                                       self.color_fk,
                                       "sphere",
                                       w=1 * self.size,
                                       tp=self.parentCtlTag)
        self.eye_npo = primitive.addTransform(self.root,
                                              self.getName("eye_npo"),
                                              t)
        self.eyeFK_ctl = self.addCtl(self.eye_npo,
                                     "fk_ctl",
                                     t,
                                     self.color_fk,
                                     "arrow",
                                     w=1 * self.size,
                                     tp=self.eyeOver_ctl)

        # look at
        t = transform.getTransformFromPos(self.guide.pos["look"])
        self.ik_cns = primitive.addTransform(
            self.root, self.getName("ik_cns"), t)

        self.eyeIK_npo = primitive.addTransform(
            self.ik_cns, self.getName("ik_npo"), t)

        self.eyeIK_ctl = self.addCtl(self.eyeIK_npo,
                                     "ik_ctl",
                                     t,
                                     self.color_fk,
                                     "circle",
                                     w=.5 * self.size,
                                     tp=self.eyeFK_ctl,
                                     ro=datatypes.Vector([1.5708, 0, 0]))
        attribute.setKeyableAttributes(self.eyeIK_ctl, self.t_params)

        t = self.guide.tra["root"]
        self.pull_srt = primitive.addTransform(self.eyeOver_ctl,
                                               self.getName('pull_srt'),
                                               t)

        t = self.guide.tra["lids"]
        self.lids_srt = primitive.addTransform(self.pull_srt,
                                               self.getName('lids_srt'),
                                               t)
        if local:
            self.lids_srt.inheritsTransform.set(0)

        self.topLids=[]
        self.topEnds=[]
        self.btmLids=[]
        self.btmEnds=[]
        for key in ['topLid1', 'topLid2', 'topLid3', 'btmLid1', 'btmLid2', 'btmLid3']:
            pos = self.guide.pos['root']
            #

            # Lookat should be (0, localPosY, localPosZ) * lids worldMtx

            #
            localV = datatypes.VectorN(self.guide.pos[key][0],
                                       self.guide.pos[key][1],
                                       self.guide.pos[key][2],
                                       1.0)
            m = self.guide.tra['lids']
            localV = localV*m.inverse()
            localV[0] = 0
            localV = localV*self.guide.tra['lids']
            lookat = datatypes.Vector(localV[0], localV[1], localV[2])
            normal = mathUtils.getMatrixAxisAsVector(self.lids_srt.worldMatrix[0], 'y')
            t = transform.getTransformLookingAt(pos, lookat, normal, axis="zy", negate=False)
            node = (primitive.addTransform(self.lids_srt, self.getName('%s_srt' % key), t))
            t = transform.setMatrixPosition(t, self.guide.pos[key])
            end = (primitive.addTransform(node, self.getName('%s_end_srt' % key), t))
            if 'top' in key:
                self.topLids.append(node)
                self.topEnds.append(end)
            else:
                self.btmLids.append(node)
                self.btmEnds.append(end)

        self.jnt_pos.append([self.eyeFK_ctl, "eye", "parent_relative_jnt"])
        self.jnt_pos.append(
            [self.pull_srt, "eyePull", "parent_relative_jnt", False])
        for end in self.topEnds + self.btmEnds:
            self.jnt_pos.append([end, end.name().replace('_end_srt', ''), "parent_relative_jnt"])

    # =====================================================
    # ATTRIBUTES
    # =====================================================
    def addAttributes(self):
        """Create the anim and setupr rig attributes for the component"""

        # Ref
        if self.settings["ikrefarray"]:
            ref_names = self.get_valid_alias_list(
                self.settings["ikrefarray"].split(","))
            if len(ref_names) > 1:
                self.ikref_att = self.addAnimEnumParam(
                    "ikref",
                    "Ik Ref",
                    0,
                    ref_names)

        # Extra custom attrs
        host =  self.eyeFK_ctl
        pm.addAttr(host, ln='pull_h', at=float, k=1, h=0, minValue=0, maxValue=1)
        pm.addAttr(host, ln='pull_v', at=float, k=1, h=0, minValue=0, maxValue=1)

        pm.addAttr(host, ln='top_ud', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='top_inner_ud', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='top_mid_ud', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='top_outer_ud', at='doubleAngle', k=1, h=0)

        pm.addAttr(host, ln='btm_ud', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='btm_inner_ud', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='btm_mid_ud', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='btm_outer_ud', at='doubleAngle', k=1, h=0)

        pm.addAttr(host, ln='blink', at=float, k=1, h=0, minValue=0, maxValue=1)
        pm.addAttr(host, ln='blink_height', at=float, k=1, h=0, minValue=0, maxValue=1)

        pm.addAttr(host, ln='auto_lids', at=float, k=1, h=0, minValue=0, maxValue=1)


    # =====================================================
    # OPERATORS
    # =====================================================
    def addOperators(self):
        """Create operators and set the relations for the component rig

        Apply operators, constraints, expressions to the hierarchy.
        In order to keep the code clean and easier to debug,
        we shouldn't create any new object in this method.

        """

        upvDir = self.settings["upVectorDirection"]
        if upvDir == 0:
            upvVec = [1, 0, 0]
        elif upvDir == 1:
            upvVec = [0, 1, 0]
        else:
            upvVec = [0, 0, 1]

        applyop.aimCns(
            self.eye_npo, self.eyeIK_ctl, "zy", 2, upvVec, self.root, False)

        pm.scaleConstraint(
            self.eyeOver_ctl, self.eye_npo, maintainOffset=False)
        pm.pointConstraint(
            self.eyeOver_ctl, self.eye_npo, maintainOffset=False)

        # Drive Eye pull
        localEyeRot = mathUtils.multiplyMatrices([self.eyeFK_ctl.worldMatrix[0],
                                                  self.eyeOver_ctl.worldInverseMatrix[0]],
                                                 name=self.getName('localEyeRot_mtx_utl'))

        eyeRotDm = mathUtils.decomposeMatrix(localEyeRot.matrixSum,
                                             name=self.getName('localEyeRot_mtx2Srt_utl'))

        eyePullHMult = mathUtils.multiply(eyeRotDm.outputRotateY,
                                          self.eyeFK_ctl.pull_h,
                                          name=self.getName('pullH_mult_utl'))

        eyePullVMult = mathUtils.multiply(eyeRotDm.outputRotateX,
                                          self.eyeFK_ctl.pull_v,
                                          name=self.getName('pullV_mult_utl'))

        eyePullHMult.output.connect(self.pull_srt.ry)
        eyePullVMult.output.connect(self.pull_srt.rx)

        # Set up lids
        blink_height_inv = mathUtils.reverse(self.eyeFK_ctl.blink_height,
                                             name=self.getName('blinkHeight_reverse_utl'))
        blink_inv = mathUtils.reverse(self.eyeFK_ctl.blink,
                                      name=self.getName('blink_reverse_utl'))

        topMax = min([abs(node.rx.get()) for node in self.topLids])
        btmMax = max([abs(node.rx.get()) for node in self.btmLids])

        def _lidsRotationSetup(topSrt, btmSrt, zone='inner'):
            '''
            for each in topSrt and btmSrt:
                creates an animBlendNodeAdditiveDA to add lid_ud and lidPart_ud values
                creates another animBlendNodeAdditiveDA to add in the default/zero rotation
            a third animBlendNodeAdditiveDA mixes the results according to blink height
            one final animBlendNodeAdditiveDA for each srt blends between their total and the blended blin value
            '''
            topZoneAttr = pm.Attribute('%s.top_%s_ud' % (self.eyeFK_ctl.name(), zone))
            btmZoneAttr = pm.Attribute('%s.btm_%s_ud' % (self.eyeFK_ctl.name(), zone))

            defaultTopRot = topSrt.rx.get()
            defaultBtmRot = btmSrt.rx.get()
            topWeight, btmWeight = 1.0, 1.0
            if topMax > 0:
                topWeight = defaultTopRot / topMax
            if btmMax > 0:
                btmWeight = defaultBtmRot / btmMax

            top_ud_sum = mathUtils.addAngles(topZoneAttr, self.eyeFK_ctl.top_ud,
                                             name=self.getName('top_%s_ud_sum_utl' % zone))
            top_ud_sum.weightB.set(topWeight)

            top_auto_sum = mathUtils.addAngles(eyeRotDm.outputRotateX, topSrt.rx.get(),
                                             name=self.getName('top_%s_auto_sum_utl' % zone))

            self.eyeFK_ctl.auto_lids.connect(top_auto_sum.weightA)

            top_sum = mathUtils.addAngles(top_ud_sum.output, top_auto_sum.output,
                                          name=self.getName('top_%s_sum_utl' % zone))

            btm_ud_sum = mathUtils.addAngles(btmZoneAttr, self.eyeFK_ctl.btm_ud,
                                             name=self.getName('btm_%s_ud_sum_utl' % zone))
            btm_ud_sum.weightB.set(btmWeight)

            btm_auto_sum = mathUtils.addAngles(eyeRotDm.outputRotateX, btmSrt.rx.get(),
                                             name=self.getName('btm_%s_auto_sum_utl' % zone))

            self.eyeFK_ctl.auto_lids.connect(btm_auto_sum.weightA)

            btm_sum = mathUtils.addAngles(btm_ud_sum.output, btm_auto_sum.output,
                                          name=self.getName('btm_%s_sum_utl' % zone))

            blink = mathUtils.blendAngles(top_sum.output, btm_sum.output,
                                          blink_height_inv.outputX, self.eyeFK_ctl.blink_height)

            top_blink = mathUtils.blendAngles(top_sum.output, blink.output, blink_inv.outputX, self.eyeFK_ctl.blink,
                                              name=self.getName('top_blink_utl'))
            btm_blink = mathUtils.blendAngles(btm_sum.output, blink.output, blink_inv.outputX, self.eyeFK_ctl.blink,
                                              name=self.getName('btm_blink_utl'))
            top_blink.output.connect(topSrt.rx)
            btm_blink.output.connect(btmSrt.rx)

        zones = ['inner', 'mid', 'outer']

        #if self.side == 'R':
        #    zones = ['outer', 'mid', 'inner']

        for topSrt, btmSrt, zone in zip(self.topLids, self.btmLids, zones):
            _lidsRotationSetup(topSrt, btmSrt, zone)



    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        """Set the relation beetween object from guide to rig"""
        self.relatives["root"] = self.eyeFK_ctl
        self.relatives["look"] = self.eyeOver_ctl

        self.controlRelatives["root"] = self.eyeFK_ctl
        self.controlRelatives["look"] = self.eyeOver_ctl

        self.jointRelatives["root"] = 0
        self.jointRelatives["look"] = 1

        self.aliasRelatives["root"] = "eye"
        self.aliasRelatives["look"] = "eyeOver"

    def connect_standard(self):
        """standard connection definition for the component"""
        self.connect_standardWithSimpleIkRef()
