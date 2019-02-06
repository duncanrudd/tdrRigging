import pymel.core as pmc
import transformUtils

reload(transformUtils)

##
# CONFIG - DICTIONARIES THAT CAN BE DUPLICATED TO CREATE VARIATIONS OF THINGS SUCH AS CONTROL COLOURS
##
colorDict = {
                   'center':14, # green
                   'right':13, # red
                   'left':6, # blue
                   'red':13,
                   'blue':6,
                   'yellow':17,
                   'green':14,
                   'purple':9,
                   'cn':14, # green
                   'rt':13, # red
                   'lf':6, # blue
                  }

def getShape(transform=None):
    '''
    returns the first shape of the specified transform

    '''
    shape = pmc.listRelatives(transform, children=1, shapes=1)[0]
    return shape

def getAllShapes(transform=None):
    '''
    returns the first shape of the specified transform

    '''
    shapes = pmc.listRelatives(transform, children=1, shapes=1)
    return shapes

def colorize( color=None, nodeList=[] ):
    '''
    takes a node ( or list or nodes ) and enables the drawing overrides.
    'Color' specifies either an integer for the required color or a string corresponding to a key in colorDict
    if nodelist is not supplied, will attempt to work on selected nodes.
    '''
    if not color:
        raise RuntimeError, 'color not specified. You must supply either a string or integer.'

    if type(color) == type('hello') or type(color) == type(u'hello'):
        color = colorDict[color]

    if not nodeList:
        nodeList = pmc.selected()
    if type(nodeList) == type('hello') or type(nodeList) == type(u'hello'):
        nodeList = [pmc.PyNode(nodeList)]

    for n in nodeList:
        n.overrideEnabled.set(1)
        n.overrideColor.set(color)

def addChild(parent, childType, name, zero=1):
    '''
    adds a new node of type childType. Parents it to the parent node.
    :param childType: 'group', 'joint', 'locator'
    :return: newly created child node
    '''
    node = None
    if childType == 'group':
        node = pmc.group(empty=1, name=name)
        node.setParent(parent)
    elif childType == 'locator':
        node = pmc.spaceLocator(name=name)
        node.setParent(parent)
    elif childType == 'joint':
        node = pmc.joint(name=name)
        if not node.getParent() == parent:
            node.setParent(parent)
    if node:
        if zero:
            transformUtils.align(node, parent)
        return node
    else:
        return 'addChild: node not created'


def addParent(child, parentType, name, zero=1):
    '''
    adds a new node of type parentType. Parents node to it.
    :param childType: 'group', 'joint', 'locator'
    :return: newly created parent node
    '''
    node = None
    if not child:
        child = pmc.selected()[0]

    parent = pmc.listRelatives(child, p=1, fullPath=1)
    if type(parent) == type([]):
        if len(parent) > 0:
            parent = parent[0]

    if parentType == 'group':
        node = pmc.group(empty=1, name=name)
    elif parentType == 'locator':
        node = pmc.spaceLocator(name=name)

    if node:
        if zero:
            transformUtils.align(node, child)
        if parent:
            node.setParent(parent)
        child.setParent(node)
        return node
    else:
        return 'addParent: node not created'