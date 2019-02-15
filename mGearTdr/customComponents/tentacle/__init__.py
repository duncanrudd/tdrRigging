"""Component Chain 01 module"""

import pymel.core as pm
from pymel.core import datatypes

from mgear.shifter import component

from mgear.core import node, applyop, vector
from mgear.core import attribute, transform, primitive

from tdrRigging.utils import curveUtils
reload(curveUtils)

##########################################################
# COMPONENT
##########################################################

numSamples=50


class Component(component.Main):
    """Shifter component Class"""

    # =====================================================
    # OBJECTS
    # =====================================================
    def addObjects(self):
        """Add all the objects needed to create the component."""

        self.normal = self.guide.blades["blade"].z * -1
        self.binormal = self.guide.blades["blade"].x
        self.WIP = self.options["mode"]

        self.noXForm = pm.createNode('transform', name=self.getName('noXForm'))
        self.noXForm.setParent(self.root)
        self.noXForm.inheritsTransform.set(0)

        # IK controllers ------------------------------------
        self.ik_npo = []
        self.ik_ctl = []
        self.ik_ref = []
        self.ik_off = []
        t = self.guide.tra["root"]
        t = transform.getTransformLookingAt(self.guide.apos[0],
                                            self.guide.apos[1],
                                            -self.normal, "xz",
                                            self.negate)
        self.ik_cns = primitive.addTransform(
            self.root, self.getName("ik_cns"), t)
        t = self.guide.tra["root"]
        self.fk_cns = primitive.addTransform(
            self.root, self.getName("fk_cns"), t)
        self.fk_cns.inheritsTransform.set(0)
        self.fk_cns.r.set(0, 0, 0)

        self.previusTag = self.parentCtlTag

        for i, v in enumerate(self.guide.apos):
            num = str(i+1).zfill(2)
            t = transform.getTransformFromPos(v)
            npo = primitive.addTransform(self.ik_cns, self.getName('ik_%s_zeroSrt' % num), t)
            npo.r.set((0, 0, 0))
            self.ik_npo.append(npo)
            ctl = self.addCtl(
                npo,
                "ik_%s_ctl" % num,
                t,
                self.color_ik,
                "square",
                h=self.size * .25,
                w=self.size * .25,
                tp=self.previusTag)
            ctl.r.set(0,0,0)
            self.ik_ctl.append(ctl)
            self.previusTag = ctl

        # Curves --------------------------------------
        self.ikCrv = curveUtils.curveThroughPoints(positions=self.guide.apos,
                                                   name=self.getName('ik_crv'),
                                                   degree=2,
                                                   rebuild=1)
        self.ikCrv.setParent(self.noXForm)

        guidePositions = [(i, 0, 0) for i in range(numSamples)]
        self.ikRailCrv = curveUtils.curveThroughPoints(positions=guidePositions,
                                                   name=self.getName('ik_rail_crv'),
                                                   degree=1,
                                                   rebuild=1)
        self.ikRailCrv.setParent(self.noXForm)

        fkPositions = [(i, 0, 0) for i in range(self.settings['num_fk_ctls'])]
        self.fkCrv = curveUtils.curveThroughPoints(positions=fkPositions,
                                                   name=self.getName('fk_crv'),
                                                   degree=2,
                                                   rebuild=1)
        self.fkCrv.setParent(self.noXForm)


        self.fkRailCrv = curveUtils.curveThroughPoints(positions=fkPositions,
                                                   name=self.getName('fk_rail_crv'),
                                                   degree=2,
                                                   rebuild=1)
        sinePositions = [(i, 0, 0) for i in range(self.settings['num_joints'])]
        self.sineCrv = curveUtils.curveThroughPoints(positions=sinePositions,
                                                   name=self.getName('sine_crv'),
                                                   degree=1,
                                                   rebuild=0)
        self.sineCrv.setParent(self.noXForm)

        # Start and end aimers ---------------------------------
        self.aim_loc = pm.spaceLocator(name=self.getName('start_aim_loc'))
        self.aim_loc.setParent(self.ik_cns)
        self.aim_end_loc = pm.spaceLocator(name=self.getName('end_aim_loc'))
        self.aim_end_loc.setParent(self.ik_ctl[-1])
        self.aim_end_loc.t.set((0, 0, 0))

        # FK ctls -------------------------------------
        self.fk_npo = []
        self.fk_ctl = []
        self.fk_avg = []
        self.previusTag = self.parentCtlTag
        for i in range(self.settings['num_fk_ctls']):
            num = str(i+1).zfill(2)
            npo = primitive.addTransform(self.fk_cns, self.getName('fk_%s_zeroSrt' % num), t)
            self.fk_npo.append(npo)
            ctl = self.addCtl(
                npo,
                "fk_%s_ctl" % num,
                t,
                self.color_fk,
                "circle",
                r=self.size * .05,
                tp=self.previusTag)
            self.fk_ctl.append(ctl)
            self.previusTag = ctl
            avg = pm.createNode('transform', name=self.getName('fk_%s_avgSrt' % num))
            avg.setParent(npo)
            avg.t.set(0, 0, 0)
            self.fk_avg.append(avg)


    # =====================================================
    # ATTRIBUTES
    # =====================================================
    def addAttributes(self):
        """Create the anim and setupr rig attributes for the component"""

        # Anim -------------------------------------------
        host = self.getHost()
        if not host:
            host = self.root
        pm.addAttr(host, ln='stretch', at='float', k=1, h=0, minValue=0, maxValue=1)
        pm.addAttr(host, ln='grow', at='float', k=1, h=0, minValue=0, maxValue=1, defaultValue=1.0)
        pm.addAttr(host, ln='twist', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='roll', at='doubleAngle', k=1, h=0)
        pm.addAttr(host, ln='sine_amplitude', at='float', k=1, h=0)
        pm.addAttr(host, ln='sine_wavelength', at='float', k=1, h=0)
        pm.addAttr(host, ln='sine_decay', at='float', k=1, h=0, minValue=0, maxValue=1)
        pm.addAttr(host, ln='sine_centre', at='float', k=1, h=0, minValue=0, maxValue=1, defaultValue=.5)
        pm.addAttr(host, ln='sine_offset', at='float', k=1, h=0)
        pm.addAttr(host, ln='sine_roll', at='doubleAngle', k=1, h=0)
        for node in self.fk_ctl:
            pm.addAttr(node, ln='roll', at='doubleAngle', k=1, h=0)
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

    # =====================================================
    # OPERATORS
    # =====================================================
    def addOperators(self):
        """Create operators and set the relations for the component rig

        Apply operators, constraints, expressions to the hierarchy.
        In order to keep the code clean and easier to debug,
        we shouldn't create any new object in this method.

        """
        host = self.getHost()
        if not host:
            host = self.root
        # IK Chain -----------------------------------------
        # Drive ik crv points
        self.dm = []
        for i in range(len(self.ik_ctl)):
            num = str(i+1).zfill(2)
            d = pm.createNode('decomposeMatrix', name=self.getName('ikCtl_%s_worldMtx2Srt_utl' % num))
            self.ik_ctl[i].worldMatrix[0].connect(d.inputMatrix)
            d.outputTranslate.connect(self.ikCrv.controlPoints[i])
            self.dm.append(d)

        # Drive aimers --------------------------------------
        ang = pm.createNode('angleBetween', name=self.getName('_startAim_angle_utl'))
        startLocalVec = pm.createNode('vectorProduct', name=self.getName('_startVec_utl'))
        self.dm[1].outputTranslate.connect(startLocalVec.input1)
        self.ik_cns.worldInverseMatrix[0].connect(startLocalVec.matrix)
        startLocalVec.operation.set(4)
        startLocalVec.output.connect(ang.vector2)
        ang.vector1.set(1, 0, 0)
        ang.euler.connect(self.aim_loc.r)

        ang = pm.createNode('angleBetween', name=self.getName('_endAim_angle_utl'))
        endLocalVec = pm.createNode('vectorProduct', name=self.getName('_endVec_utl'))
        self.dm[-2].outputTranslate.connect(endLocalVec.input1)
        self.ik_ctl[-1].worldInverseMatrix[0].connect(endLocalVec.matrix)
        endLocalVec.operation.set(4)
        endLocalVec.output.connect(ang.vector2)
        ang.vector1.set(-1, 0, 0)
        ang.euler.connect(self.aim_end_loc.r)

        # Drive ik rail points -----------------------------
        self.ikRailMp = []
        for i in range(numSamples):
            num = str(i+1).zfill(2)
            param = (1.0 / (numSamples-1)) * i
            mp = pm.createNode('motionPath', name=self.getName('ikCrv_%s_mp_utl' % num))
            self.ikCrv.worldSpace[0].connect(mp.geometryPath)
            mp.uValue.set(param)
            mp.fractionMode.set(1)
            mp.frontAxis.set(0)
            mp.upAxis.set(1)
            mp.follow.set(1)
            mp.worldUpType.set(2)
            vp = pm.createNode('vectorProduct', name=self.getName('ikRail_%s_upVec_utl' % num))
            vp.operation.set(3)
            vp.normalizeOutput.set(1)
            vp.input1Y.set(1)
            if not i:
                self.aim_loc.worldMatrix[0].connect(mp.worldUpMatrix)
                self.aim_loc.worldMatrix[0].connect(vp.matrix)
            else:
                self.ikRailMp[-1].orientMatrix.connect(vp.matrix)
                self.ikRailMp[-1].orientMatrix.connect(mp.worldUpMatrix)
            pma = pm.createNode('plusMinusAverage', name=self.getName('ikRail_%s_pos_utl' % num))
            md = pm.createNode('multiplyDivide', name=self.getName('ikRail_%s_upVecMult_utl' % num))
            md.input2.set((.1, .1, .1))
            vp.output.connect(md.input1)
            md.output.connect(pma.input3D[0])
            mp.allCoordinates.connect(pma.input3D[1])
            pma.output3D.connect(self.ikRailCrv.controlPoints[i])
            self.ikRailMp.append(mp)

        # Twist --------------------------------------------
        mpUp = pm.createNode('motionPath', name=self.getName('twist_upMp_utl'))
        self.ikRailCrv.worldSpace[0].connect(mpUp.geometryPath)
        mpUp.uValue.set(1.0)

        twistVec = pm.createNode('vectorProduct', name=self.getName('twistVec_utl'))
        mpUp.allCoordinates.connect(twistVec.input1)
        self.aim_end_loc.worldInverseMatrix[0].connect(twistVec.matrix)
        twistVec.operation.set(4)

        twistAng = pm.createNode('angleBetween', name=self.getName('twistAngle_utl'))
        twistVec.output.connect(twistAng.vector1)
        twistAng.vector2.set(0, 1, 0)
        twistSign = pm.createNode('condition', name=self.getName('twistSign_utl'))
        twistVec.outputZ.connect(twistSign.firstTerm)
        twistSign.operation.set(2)
        twistSign.colorIfTrueR.set(-1)
        signedTwist = pm.createNode('animBlendNodeAdditiveDA', name=self.getName('twistResult_utl'))
        twistAng.angle.connect(signedTwist.inputA)
        twistSign.outColorR.connect(signedTwist.weightA)

        # FK Chain -----------------------------------------
        self.fk_mtx = []
        print 'fk mpo: %s' % self.fk_npo
        for i in range(self.settings['num_fk_ctls']):
            num = str(i + 1).zfill(2)
            param = (1.0 / (self.settings['num_fk_ctls']-1)) * i
            mp = pm.createNode('motionPath', name=self.getName('ikCrv_%s_mp_utl' % num))
            mp.fractionMode.set(1)
            mp.follow.set(1)
            mp.frontAxis.set(0)
            mp.upAxis.set(1)
            mp.worldUpType.set(1)
            self.ikCrv.worldSpace[0].connect(mp.geometryPath)
            mp.uValue.set(param)

            mpUp = pm.createNode('motionPath', name=self.getName('ikCrv_%s_mp_utl' % num))
            self.ikRailCrv.worldSpace[0].connect(mpUp.geometryPath)
            mpUp.uValue.set(param)
            mtxUp = pm.createNode('composeMatrix', name=self.getName('ikCrv_%s_upMtx_utl' % num))
            mpUp.allCoordinates.connect(mtxUp.inputTranslate)
            mtxUp.outputMatrix.connect(mp.worldUpMatrix)

            wMtx = pm.createNode('composeMatrix', name=self.getName('ikCrv_%s_worldMtx_utl' % num))
            mp.allCoordinates.connect(wMtx.inputTranslate)
            mp.rotate.connect(wMtx.inputRotate)
            self.fk_mtx.append(wMtx)

            if not i:
                mp.allCoordinates.connect(self.fk_npo[i].t)
                mp.rotate.connect(self.fk_npo[i].r)
            else:
                localMtx = pm.createNode('multMatrix', name=self.getName('ikCrv_%s_localMtx_utl' % num))
                wMtx.outputMatrix.connect(localMtx.matrixIn[0])
                iMtx = pm.createNode('inverseMatrix', name='ikCrv_%s_worldInverseMtx_utl' % num)
                self.fk_mtx[i-1].outputMatrix.connect(iMtx.inputMatrix)
                iMtx.outputMatrix.connect(localMtx.matrixIn[1])
                self.fk_ctl[i-1].worldMatrix[0].connect(localMtx.matrixIn[2])
                d = pm.createNode('decomposeMatrix', name=self.getName('ikCrv_%s_mtx2Srt_utl' % num))
                localMtx.matrixSum.connect(d.inputMatrix)
                d.outputTranslate.connect(self.fk_npo[i].t)
                d.outputRotate.connect(self.fk_npo[i].r)

                twistMult = pm.createNode('animBlendNodeAdditiveDA', name=self.getName('ikCrv_%s_twistMult_utl' % num))
                twistMult.weightA.set((1.0 / (self.settings['num_fk_ctls']-1)) * i)
                signedTwist.output.connect(twistMult.inputA)
                twistMult.output.connect(mp.frontTwist)

        # Drive fk crv points
        self.fk_dm = []
        for i in range(len(self.fk_ctl)):
            num = str(i + 1).zfill(2)
            d = pm.createNode('decomposeMatrix', name=self.getName('fkCtl_%s_worldMtx2Srt_utl' % num))
            self.fk_ctl[i].worldMatrix[0].connect(d.inputMatrix)
            d.outputTranslate.connect(self.fkCrv.controlPoints[i])
            self.fk_dm.append(d)

            # Drive avg nodes
            pb = pm.createNode('pairBlend', name=self.getName('fkAvg_%s_utl' % num))
            self.fk_ctl[i].r.connect(pb.inRotate2)
            self.fk_ctl[i].roll.connect(pb.inRotateX1)
            pb.weight.set(0.5)
            pb.outRotate.connect(self.fk_avg[i].r)

            # FK rail crv points
            vp = pm.createNode('vectorProduct', name=self.getName('fkRailPoint_%s_utl' % num))
            self.fk_avg[i].worldMatrix[0].connect(vp.matrix)
            vp.input1.set(0, 0.1, 0)
            vp.operation.set(4)
            vp.output.connect(self.fkRailCrv.controlPoints[i])

        # Stretch --------------------------------------------
        self.crvInfo = pm.createNode('curveInfo', name=self.getName('fk_crvInfo_utl'))
        self.fkCrv.worldSpace[0].connect(self.crvInfo.inputCurve)
        stretchScaled = pm.createNode('multiplyDivide', name=self.getName('fk_crvLenScaled_utl'))
        stretchScaled.operation.set(2)
        self.dm[0].outputScaleX.connect(stretchScaled.input1X)
        self.crvInfo.arcLength.connect(stretchScaled.input2X)
        stretch = pm.createNode('multiplyDivide', name=self.getName('fk_crvStretch_utl'))
        stretchScaled.outputX.connect(stretch.input2X)
        stretch.input1X.set(self.crvInfo.arcLength.get())
        stretchClamp = pm.createNode('clamp', name=self.getName('stretchClamp_utl'))
        stretchClamp.maxR.set(1.0)
        stretch.outputX.connect(stretchClamp.inputR)

        # Sine ---------------------------------------------
        pm.select(None)
        sineDef = pm.nonLinear(self.sineCrv, type='sine', name=self.getName('sine_def'))
        sineDef[1].rz.set(-90)
        sineDef[1].setParent(self.noXForm)
        host.sine_roll.connect(sineDef[1].ry)
        sinePosMult = pm.createNode('multDoubleLinear', name=self.getName('sinePosMult_utl'))
        host.sine_centre.connect(sinePosMult.input1)
        sinePosMult.input2.set(self.settings['num_joints'])
        sinePosMult.output.connect(sineDef[1].tx)
        host.sine_decay.connect(sineDef[0].dropoff)
        host.sine_amplitude.connect(sineDef[0].amplitude)
        host.sine_wavelength.connect(sineDef[0].wavelength)
        host.sine_offset.connect(sineDef[0].offset)

        sineHighRange = pm.createNode('setRange', name=self.getName('sineHighRange_utl'))
        sineHighRange.oldMinX.set(0)
        sineHighRange.oldMaxX.set(1)
        sineHighRange.minX.set(2)
        sineHighRange.maxX.set(0)
        host.sine_centre.connect(sineHighRange.valueX)
        sineHighRange.outValueX.connect(sineDef[0].highBound)

        sineLowRange = pm.createNode('setRange', name=self.getName('sineLowRange_utl'))
        sineLowRange.oldMinX.set(0)
        sineLowRange.oldMaxX.set(1)
        sineLowRange.minX.set(0)
        sineLowRange.maxX.set(-2)
        host.sine_centre.connect(sineLowRange.valueX)
        sineLowRange.outValueX.connect(sineDef[0].lowBound)

        # Joints -------------------------------------------
        self.joints=[]
        for i in range(self.settings['num_joints']):
            num = str(i+1).zfill(2)
            # per joint stretch and grow
            param = (1.0 / (self.settings['num_joints']-1)) * i
            stretchedParam = pm.createNode('multDoubleLinear', name=self.getName('result_%s_stretchedParam_utl' % num))
            stretchedParam.input1.set(param)
            stretchClamp.outputR.connect(stretchedParam.input2)
            stretchBlend = pm.createNode('blendTwoAttr', name=self.getName('result_%s_stretchBlend_utl' % num))
            stretchedParam.input1.connect(stretchBlend.input[1])
            stretchedParam.output.connect(stretchBlend.input[0])
            host.stretch.connect(stretchBlend.attributesBlender)
            growBlend = pm.createNode('animBlendNodeAdditive', name=self.getName('result_%s_growBlend_utl' % num))
            stretchBlend.output.connect(growBlend.inputA)
            host.grow.connect(growBlend.weightA)

            # twisting and rolling
            roll = pm.createNode('animBlendNodeAdditiveDA', name=self.getName('result_%s_twist_utl' % num))
            host.roll.connect(roll.inputA)
            host.twist.connect(roll.inputB)
            growBlend.output.connect(roll.weightB)

            mp = pm.createNode('motionPath', name=self.getName('result_%s_mp_utl' % num))
            self.fkCrv.worldSpace[0].connect(mp.geometryPath)
            mp.fractionMode.set(1)
            mp.frontAxis.set(0)
            mp.upAxis.set(1)
            mp.follow.set(1)
            mp.worldUpType.set(3)
            growBlend.output.connect(mp.uValue)
            roll.output.connect(mp.frontTwist)

            mpUp = pm.createNode('motionPath', name=self.getName('result_%s_upMp_utl' % num))
            self.fkRailCrv.worldSpace[0].connect(mpUp.geometryPath)
            mpUp.fractionMode.set(1)
            growBlend.output.connect(mpUp.uValue)

            upVec = pm.createNode('plusMinusAverage', name=self.getName('result_%s_upVec_utl' % num))
            mpUp.allCoordinates.connect(upVec.input3D[0])
            mp.allCoordinates.connect(upVec.input3D[1])
            upVec.operation.set(2)
            upVec.output3D.connect(mp.worldUpVector)

            # sine wave
            sineMp = pm.createNode('motionPath', name=self.getName('sine_%s_mp_utl' % num))
            self.sineCrv.worldSpace[0].connect(sineMp.geometryPath)
            sineMp.uValue.set(i)

            j = pm.createNode('joint', name=self.getName('%s_dfm' % num))
            if not i:
                self.dm[0].outputScale.connect(j.s)
                j.setParent(self.noXForm)
                wMtx = pm.createNode('composeMatrix', name=self.getName('result_%s_worldMtx_utl' % num))
                mp.allCoordinates.connect(wMtx.inputTranslate)
                mp.rotate.connect(wMtx.inputRotate)

                localMtx = pm.createNode('multMatrix', name=self.getName('result_%s_localMtx_utl' % num))
                wMtx.outputMatrix.connect(localMtx.matrixIn[0])
                #self.root.worldInverseMatrix[0].connect(localMtx.matrixIn[1])

                d = pm.createNode('decomposeMatrix', name=self.getName('result_%s_mtx2Srt_utl' % num))
                localMtx.matrixSum.connect(d.inputMatrix)
                deformedPos = pm.createNode('plusMinusAverage', name=self.getName('result_%s_deformedPos_utl' % num))
                d.outputTranslate.connect(deformedPos.input3D[0])
                sineMp.allCoordinates.yCoordinate.connect(deformedPos.input3D[1].input3Dy)
                sineMp.allCoordinates.zCoordinate.connect(deformedPos.input3D[1].input3Dz)
                deformedPos.output3D.connect(j.t)
                d.outputRotate.connect(j.r)
            else:
                j.setParent(self.joints[-1])
                wMtx = pm.createNode('composeMatrix', name=self.getName('result_%s_worldMtx_utl' % num))
                mp.allCoordinates.connect(wMtx.inputTranslate)
                mp.rotate.connect(wMtx.inputRotate)

                localMtx = pm.createNode('multMatrix', name=self.getName('result_%s_localMtx_utl' % num))
                wMtx.outputMatrix.connect(localMtx.matrixIn[0])
                self.joints[-1].worldInverseMatrix[0].connect(localMtx.matrixIn[1])
                d = pm.createNode('decomposeMatrix', name=self.getName('result_%s_mtx2Srt_utl' % num))
                localMtx.matrixSum.connect(d.inputMatrix)
                deformedPos = pm.createNode('plusMinusAverage', name=self.getName('result_%s_deformedPos_utl' % num))
                d.outputTranslate.connect(deformedPos.input3D[0])
                sineMp.allCoordinates.yCoordinate.connect(deformedPos.input3D[1].input3Dy)
                sineMp.allCoordinates.zCoordinate.connect(deformedPos.input3D[1].input3Dz)
                deformedPos.output3D.connect(j.t)
                d.outputRotate.connect(j.r)
            j.segmentScaleCompensate.set(0)
            j.jo.set(0, 0, 0)
            self.joints.append(j)

    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        return
        """Set the relation beetween object from guide to rig"""

        self.relatives["root"] = self.loc[0]
        self.controlRelatives["root"] = self.fk_ctl[0]
        self.jointRelatives["root"] = 0
        for i in range(0, len(self.loc) - 1):
            self.relatives["%s_loc" % i] = self.loc[i + 1]
            self.controlRelatives["%s_loc" % i] = self.fk_ctl[i + 1]
            self.jointRelatives["%s_loc" % i] = i + 1
            self.aliasRelatives["%s_ctl" % i] = i + 1
        self.relatives["%s_loc" % (len(self.loc) - 1)] = self.loc[-1]
        self.controlRelatives["%s_loc" % (len(self.loc) - 1)] = self.fk_ctl[-1]
        self.jointRelatives["%s_loc" % (len(self.loc) - 1)] = len(self.loc) - 1
        self.aliasRelatives["%s_loc" % (len(self.loc) - 1)] = len(self.loc) - 1

    # @param self
    def addConnection(self):
        return
        """Add more connection definition to the set"""

        self.connections["standard"] = self.connect_standard
        self.connections["orientation"] = self.connect_orientation
        self.connections["parent"] = self.connect_parent

    def connect_orientation(self):
        """orientation connection definition for the component"""
        self.connect_orientCns()

    def connect_standard(self):
        """standard connection definition for the component"""
        self.connect_standardWithSimpleIkRef()

    def connect_parent(self):
        self.connect_standardWithSimpleIkRef()
