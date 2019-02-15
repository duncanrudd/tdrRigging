import pymel.core as pm

def addBlendedPositionJoint(srcJnt=None, tgtJnt=None, parJnt=None, name=None):
    """
    Create a joint parented to parJnt which is positioned halfway between srcJnt and tgtJnt.
    If no parent joint is supplied, srcJnt will be used as the parent

    returns the newly created joint blendPos
    """
    if not srcJnt or not tgtJnt:
        try:
            srcJnt, tgtJnt = pm.selected()[0], pm.selected()[1]
        except:
            pm.displayWarning('Please supply or select src and tgt joints. BlendedPositionJoint not created.')
            return
    if not parJnt:
        try:
            parJnt = pm.selected()[2]
        except:
            parJnt = srcJnt

    if name:
        bname = 'blendPos_' + name
    else:
        bname = 'blendPos_' + tgtJnt.name()

    jnt = pm.createNode('joint', n=bname, p=parJnt)
    jnt.attr('radius').set(1.5)

    pb = pm.createNode('pairBlend')
    pb.rotInterpolation.set(1)
    pb.weight.set(0.5)
    if tgtJnt.getParent() != srcJnt:
        m = localMtx = pm.createNode('multMatrix')
        tgtJnt.worldMatrix[0].connect(m.matrixIn[0])
        parJnt.worldInverseMatrix[0].connect(m.matrixIn[1])
        d = pm.createNode('decomposeMatrix')
        m.matrixSum.connect(d.inputMatrix)
        d.outputTranslate.connect(pb.inTranslate1)
        d.outputRotate.connect(pb.inRotate1)

        m = localMtx = pm.createNode('multMatrix')
        srcJnt.worldMatrix[0].connect(m.matrixIn[0])
        parJnt.worldInverseMatrix[0].connect(m.matrixIn[1])
        d = pm.createNode('decomposeMatrix')
        m.matrixSum.connect(d.inputMatrix)
        d.outputTranslate.connect(pb.inTranslate2)
        d.outputRotate.connect(pb.inRotate2)
    else:
        tgtJnt.t.connect(pb.inTranslate1)
        tgtJnt.r.connect(pb.inRotate1)
    pb.outTranslate.connect(jnt.t)
    #pb.outRotate.connect(jnt.r)

    jnt.attr("overrideEnabled").set(1)
    jnt.attr("overrideColor").set(17)

    jnt.attr("segmentScaleCompensate").set(0)

    try:
        defSet = pm.PyNode("rig_deformers_grp")

    except TypeError:
        pm.sets(n="rig_deformers_grp")
        defSet = pm.PyNode("rig_deformers_grp")

    pm.sets(defSet, add=jnt)

    return jnt