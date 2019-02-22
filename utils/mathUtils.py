import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.util as pmUtil
import math


# --------------------------------------------------------------------------------
# Arithmetic
# --------------------------------------------------------------------------------

def addScalar(inputs, name=None, operation=1):
    node = pm.createNode('plusMinusAverage')
    node.operation.set(operation)
    if name:
        node.rename(name)
    for index, input in zip(range(len(inputs)), inputs):
        if type(input) == pm.general.Attribute:
            input.connect(node.input1D[index])
        else:
            node.input1D[index].set(input)
    return node

def subtractScalar(inputs, name=None):
    return addScalar(inputs, name, operation=2)

def reverse(input, name=None):
    node = pm.createNode('reverse')
    if name:
        node.rename(name)
    if type(input) == pm.general.Attribute:
        input.connect(node.inputX)
    else:
        node.inputX.set(input)
    return node

def addAngles(inputA, inputB, name=None):
    '''
    creates an animBlendNodeAdditiveDA node and connects input1 and input2
    '''
    node = pm.createNode('animBlendNodeAdditiveDA')
    if name:
        node.rename(name)
    if type(inputA) == pm.general.Attribute:
        inputA.connect(node.inputA)
    else:
        node.inputA.set(inputA)

    if type(inputB) == pm.general.Attribute:
        inputB.connect(node.inputB)
    else:
        node.inputB.set(inputB)
    return node

def blendAngles(inputA, inputB, weightA, weightB, name=None):
    '''
    calls addAngles function above and adds options to control weights of inputs
    '''
    node = addAngles(inputA, inputB, name)
    if type(weightA) == pm.general.Attribute:
        weightA.connect(node.weightA)
    else:
        node.weightA.set(weightA)

    if type(weightB) == pm.general.Attribute:
        weightB.connect(node.weightB)
    else:
        node.weightB.set(weightB)
    return node

def getAngleBetweenVectors(v1, v2, vUp, degrees=1):
    '''
    returns the signed angle between v1 and v2
    '''
    if not type(v1) == dt.Vector:
        v1 = dt.Vector(v1)
    if not type(v2) == dt.Vector:
        v2 = dt.Vector(v2)
    if not type(vUp) == dt.Vector:
        vUp = dt.Vector(vUp)
    angle = v1.angle(v2)
    dot = vUp.dot(v2)
    if dot < 0:
        angle *= -1
    if degrees:
        angle = pmUtil.degrees(angle)
    return angle

def multiply(input1, input2, name=None):
    mult = pm.createNode('multDoubleLinear')
    if name:
        mult.rename(name)
    if type(input1) == pm.general.Attribute:
        val = input1.get()
        connect=True
    else:
        val = input1
        connect=False

    if connect:
        input1.connect(mult.input1)
    else:
        mult.input1.set(input1)

    if type(input2) == pm.general.Attribute:
        val = input2.get()
        connect=True
    else:
        val = input2
        connect=False

    if connect:
        input2.connect(mult.input2)
    else:
        mult.input2.set(input2)
    return mult

def multiplyVector(input1, input2, name=None, operation=1):
    md = pm.createNode('multiplyDivide', name=name)
    md.operation.set(operation)

    val = 0.0
    connect = False

    if type(input1) == pm.general.Attribute:
        val = input1.get()
        connect = True
    else:
        val = input1
        connect = False

    if type(val) == pm.datatypes.Vector or type(val) == tuple:
        if connect:
            input1.connect(md.input1)
        else:
            md.input1.set(input1)
    else:
        if connect:
            input1.connect(md.input1X)
        else:
            md.input1X.set(input1)

    if type(input2) == pm.general.Attribute:
        val = input2.get()
        connect = True
    else:
        val = input2
        connect = False

    if type(val) == pm.datatypes.Vector or type(val) == tuple:
        if connect:
            input2.connect(md.input2)
        else:
            md.input2.set(input2)
    else:
        if connect:
            input2.connect(md.input2X)
        else:
            md.input2X.set(input2)

    return md

def divide(input1, input2, name=None):
    return multiplyVector(input1, input2, name, operation=2)

def multiplyRotationByScalar(input1, factor, name=None):
    node = pm.createNode('animBlendNodeAdditiveRotation')
    if name:
        node.rename(name)
    if type(input1) == pm.general.Attribute:
        input1.connect(node.inputA)
    else:
        node.inputA.set(input1)
    if type(factor) == pm.general.Attribute:
        factor.connect(node.weightA)
    else:
        node.weightA.set(factor)
    return node

# -----------------------------------------------------------------------
# MATRIX OPS
# -----------------------------------------------------------------------

axisDict = {'x': 0, 'y': 1, 'z': 2, '-x': 0, '-y': 1, '-z': 2}

def getMatrixAxisAsVector(mtx, axis):
    '''
    returns a vector representing the supplied axis of mtx
    '''
    if type(mtx) == pm.general.Attribute:
        mtx = mtx.get()
    row = None
    if 'x' in axis:
        row = dt.Vector((mtx.a00, mtx.a01, mtx.a02))
    elif 'y' in axis:
        row = dt.Vector((mtx.a10, mtx.a11, mtx.a12))
    else:
        row = dt.Vector((mtx.a20, mtx.a21, mtx.a22))
    return row

def multiplyMatrices(mtxList, name=None):
    '''
    Creates a multMatrix node and connects each mtx in mtxList in order
    Returns newly created multMatrix node
    '''
    mtx = pm.createNode('multMatrix')
    if name:
        mtx.rename(name)
    for i in range(len(mtxList)):
        mtxList[i].connect(mtx.matrixIn[i])
    return mtx

def decomposeMatrix(mtx, name=None):
    dm = pm.createNode('decomposeMatrix')
    if name:
        dm.rename(name)
    mtx.connect(dm.inputMatrix)
    return dm

def getTransformedPoint(point, matrix):
    point = dt.VectorN(point[0], point[1], point[2], 1.0)
    if type(matrix) == type([]):
        matrix = dt.Matrix(matrix)
    point = point * matrix
    return dt.Vector(point[0], point[1], point[2])

def createTransformedPoint(point, matrix, name=None):
    node = pm.createNode('vectorProduct')
    if name:
        node.rename(name)
    if type(point) == pm.general.Attribute:
        point.connect(node.input1)
    else:
        node.input1.set(point)
    matrix.connect(node.matrix)
    node.operation.set(4)
    return node

def createComposeMatrix(inputTranslate=(0,0,0), inputRotate=(0,0,0), inputScale=(1,1,1), name=None):
    node = pm.createNode('composeMatrix')
    if name:
        node.rename(name)

    if type(inputTranslate) == pm.general.Attribute:
        inputTranslate.connect(node.inputTranslate)
    else:
        node.inputTranslate.set(inputTranslate)

    if type(inputRotate) == pm.general.Attribute:
        inputRotate.connect(node.inputRotate)
    else:
        node.inputRotate.set(inputRotate)

    if type(inputScale) == pm.general.Attribute:
        inputScale.connect(node.inputScale)
    else:
        node.inputScale.set(inputScale)
    return node

def inverseMatrix(matrix, name=None):
    node = pm.createNode('inverseMatrix')
    if name:
        node.rename(name)
    matrix.connect(node.inputMatrix)
    return node


# -----------------------------------------------------------------------
# VECTOR OPS
# -----------------------------------------------------------------------

def getStartAndEnd(start=None, end=None):
    '''
    Takes either two pynodes, two vectors or two selected nodes and returns their positions
    '''
    startPos, endPos = None, None
    if not start or not end:
        if len(pm.selected()) == 2:
            startPos = pm.xform(pm.selected()[0], translation=True, query=True, ws=True)
            endPos = pm.xform(pm.selected()[1], translation=True, query=True, ws=True)
    else:
        if pm.nodetypes.Transform in type(start).__mro__:
            startPos = pm.xform(start, translation=True, query=True, ws=True)
        else:
            startPos = start

        if pm.nodetypes.Transform in type(end).__mro__:
            endPos = pm.xform(end, translation=True, query=True, ws=True)
        else:
            endPos = end

    if not startPos or not endPos:
        return (None, None)
    else:
        return startPos, endPos

def getDistance(start, end):
    '''
    Calculates distance between two Transforms using magnitude
    '''

    def mag(numbers):
        num = 0
        for eachNumber in numbers:
            num += math.pow(eachNumber, 2)

        mag = math.sqrt(num)
        return mag

    startPos, endPos = getStartAndEnd(start, end)

    if not startPos or not endPos:
        return 'getDistance: Cannot determine start and end points'

    calc = []
    calc.append(startPos[0] - endPos[0])
    calc.append(startPos[1] - endPos[1])
    calc.append(startPos[2] - endPos[2])

    return mag(calc)

# -----------------------------------------------------------------------
# MISC
# -----------------------------------------------------------------------
def clamp(input, min, max, name=None):
    node = pm.createNode('clamp')
    if name:
        node.rename(name)
    input.connect(node.inputR)
    if type(min) == pm.general.Attribute:
        min.connect(node.minR)
    else:
        node.minR.set(min)
    if type(max) == pm.general.Attribute:
        max.connect(node.maxR)
    else:
        node.maxR.set(max)
    return node

def blendScalarAttrs(attr1, attr2, blend, name=None):
    node = pm.createNode('blendTwoAttr')
    if name:
        node.rename(name)
    attr1.connect(node.input[0])
    attr2.connect(node.input[1])
    if type(blend) == pm.general.Attribute:
        blend.connect(node.attributesBlender)
    else:
        node.attributesBlender.set(blend)
    return node
