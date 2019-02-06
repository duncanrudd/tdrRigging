import tdrRigging.utils.dagUtils as dagUtils
import pymel.core as pmc


def orientIcon(icon=None, axis=None):
    '''
    rotates the cvs of a icon to point along axis

    '''
    # orient ik_anim cvs properly
    shape = dagUtils.getShape(icon)
    pmc.select('%s.cv[ * ]' % shape)

    if axis == 'y':
        pmc.rotate(90, rotateX=True)
    elif axis == 'x':
        pmc.rotate(90, rotateY=True)
    elif axis == 'z':
        pmc.rotate(90, rotateZ=True)
    elif axis == '-y':
        pmc.rotate(-90, rotateX=True)
    elif axis == '-x':
        pmc.rotate(-90, rotateY=True)
    elif axis == '-z':
        pmc.rotate(-90, rotateZ=True)

    pmc.select(None)


def circleIcon(radius=20.0, name='', axis='z'):
    '''
    creates a circular nurbs curve

    '''
    icon = pmc.circle(name=name, r=radius, ch=0, o=1)[0]

    if axis != 'z':
        orientIcon(icon=icon, axis=axis)
    return icon


def circleBumpIcon(radius=20.0, name='', axis='z'):
    '''
    creates a circular nurbs curve with a bump to indicate orientation

    '''
    icon = pmc.circle(name=name, r=radius, ch=0, o=1, s=24)[0]

    shape = dagUtils.getShape(icon)
    shape.rename(icon.name() + 'Shape')
    pmc.select('%s.cv[ 1 ]' % shape)
    pmc.move(radius * .5, moveY=1, r=1)
    if '-' in axis:
        pmc.select('%s.cv[*]' % shape)
        pmc.rotate(180, rotateZ=True)

    if axis != 'z':
        orientIcon(icon=icon, axis=axis)
    return icon

def hexIcon(radius=20.0, name='', axis='z'):
    '''
    creates a circular nurbs curve of degree 1 with a raised section front and rear to indicate orientation

    '''

    points = [(0, 0.2, 1.217186), (0.309017, 0.2, 0.951057), (0.309017, 0.2, 0.951057), (0.382683, 0, 0.92388), (0.382683, 0, 0.92388), (0.707107, 0, 0.707107), (0.92388, 0, 0.382683), (1, 0, 0),
              (0.92388, 0, -0.382683), (0.707107, 0, -0.707107), (0.382683, 0, -0.92388), (0.382683, 0, -0.92388), (0.309017, 0.2, -0.951057), (0.309017, 0.2, -0.951057), (0, 0.2, -1),
              (-0.309017, 0.2, -0.951057), (-0.309017, 0.2, -0.951057), (-0.382683, 0, -0.92388), (-0.382683, 0, -0.92388), (-0.707107, 0, -0.707107), (-0.92388, 0, -0.382683), (-1, 0, 0),
              (-0.92388, 0, 0.382683), (-0.707107, 0, 0.707107), (-0.382683, 0, 0.92388), (-0.382683, 0, 0.92388), (-0.309017, 0.2, 0.951057), (-0.309017, 0.2, 0.951057), (0, 0.2, 1.217186)]

    knots = [0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 26, 26]

    icon = pmc.curve(name=name, d=3,
                     p=[(point[0]*radius, point[1]*radius, point[2]*radius) for point in points],
                     k=knots)


    shape = dagUtils.getShape(icon)
    shape.rename(icon.name() + 'Shape')

    if '-' in axis:
        pmc.select('%s.cv[*]' % shape)
        pmc.rotate(180, rotateZ=True)

    if axis != 'z':
        orientIcon(icon=icon, axis=axis)
    return icon


def boxIcon(size=20.0, name=''):
    '''
    Creates a box shaped nurbs curve

    '''
    pos = size * 0.5
    neg = pos * -1
    points = [(neg, pos, neg), (neg, neg, neg), (neg, neg, pos), (neg, pos, pos),
              (neg, pos, neg), (pos, pos, neg), (pos, neg, neg), (neg, neg, neg),
              (neg, neg, pos), (pos, neg, pos), (pos, neg, neg), (pos, pos, neg),
              (pos, pos, pos), (neg, pos, pos), (pos, pos, pos), (pos, neg, pos)]

    knots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    icon = pmc.curve(degree=1, p=points, k=knots, name=name)

    return icon


def crossIcon(size=20.0, name='', axis='z'):
    '''
    Creates a locator shaped nurbs curve

    '''
    pos = size * 0.5
    neg = pos * -1
    points = [(0, 0, neg), (0, 0, pos), (0, 0, 0), (0, pos, 0),
              (0, neg, 0), (0, 0, 0), (pos, 0, 0), (neg, 0, 0)]

    knots = [1, 2, 3, 4, 5, 6, 7, 8]

    icon = pmc.curve(degree=1, p=points, k=knots, name=name)

    return icon


def squareIcon(size=20.0, name='', axis='y'):
    '''
    creates a square nurbs curve

    '''
    pos = size * 0.5
    neg = pos * -1
    points = [(neg, neg, 0), (neg, pos, 0), (pos, pos, 0), (pos, neg, 0), (neg, neg, 0)]

    knots = [1, 2, 3, 4, 5]

    icon = pmc.curve(degree=1, p=points, k=knots, name=name)
    if axis != 'z':
        orientIcon(icon=icon, axis=axis)
    return icon

def squareChamferIcon(size=20.0, name='', axis='y'):
    '''
    creates a square nurbs curve

    '''
    points = [(-1, 0, -3), (-1, 0, -4), (1, 0, -4), (1, 0, -3), (3, 0, -1), (4, 0, -1), (4, 0, 1),(3, 0, 1),
              (1, 0, 3), (1, 0, 4), (-1, 0, 4), (-1, 0, 3), (-3, 0, 1),(-4, 0, 1), (-4, 0, -1), (-3, 0, -1), (-1, 0, -3)]

    knots = [i for i in range(len(points))]

    icon = pmc.curve(degree=1, p=points, k=knots, name=name)
    shape = dagUtils.getShape(icon)
    pmc.select('%s.cv[ * ]' % shape)
    pmc.rotate(45, rotateY=True)
    pmc.scale(size*.25, size*.25, size*.25)
    if axis != 'z':
        orientIcon(icon=icon, axis=axis)
    return icon

def ballIcon(radius=20.0, name=''):
    icon = pmc.circle(name=name, r=radius, ch=0, o=1, s=8, nr=(0,1,0))[0]
    dup1 = pmc.circle(name=name, r=radius, ch=0, o=1, s=8, nr=(1,0,0))[0]
    dup2 = pmc.circle(name=name, r=radius, ch=0, o=1, s=8, nr=(0,0,1))[0]
    shape = pmc.listRelatives(dup1, shapes=True)[0]
    pmc.parent(shape, icon, s=1, r=1)
    shape = pmc.listRelatives(dup2, shapes=True)[0]
    pmc.parent(shape, icon, s=1, r=1)
    pmc.delete([dup1, dup2])

    return icon


def pinIcon(radius=20.0, name='', axis='z'):
    '''
    creates a pin control

    '''
    axisDict = {'x': (radius, 0, 0), 'y': (0, radius, 0), 'z': (0, 0, radius), '-x': (radius * -1, 0, 0),
                '-y': (0, radius * -1, 0), '-z': (0, 0, radius * -1)}
    line = pmc.curve(d=1, p=[(0, 0, 0), axisDict[axis]], k=[0, 1], name=name)

    circle = pmc.circle(name=(name + '_circle'), r=radius * .2, ch=0, o=1, s=24)
    if axis != 'z':
        orientIcon(icon=circle, axis=axis)
    shape = pmc.listRelatives(circle, shapes=True)[0]

    pmc.move(axisDict[axis][0], axisDict[axis][1], axisDict[axis][2], "%s.cv[:]" % shape, r=1)

    pmc.parent(shape, line, shape=1, r=1)
    shapes = pmc.listRelatives(line, shapes=True)
    shapes[1].rename(shapes[0].nodeName().replace('Shape', 'CircleShape'))
    pmc.delete(circle)

    return line

def triIcon(size=20.0, name='', aim='up'):
    '''
    creates a triangular nurbs curve

    '''
    points = []
    pos = size * .5
    neg = pos * -1
    if aim == 'up':
        points = [(neg, 0, 0), (pos, 0, 0), (0, size, 0), (neg, 0, 0)]
    elif aim == 'right':
        points = [(0, neg, 0), (0, pos, 0), (-size, 0, 0), (0, neg, 0)]
    elif aim == 'left':
        points = [(0, neg, 0), (0, pos, 0), (size, 0, 0), (0, neg, 0)]
    elif aim == 'down':
        points = [(neg, 0, 0), (pos, 0, 0), (0, -size, 0), (neg, 0, 0)]

    knots = [1, 2, 3, 4]
    if points:
        icon = pmc.curve(degree=1, p=points, k=knots, name=name)
        return icon
    else:
        return 'please supply an aim: up, down, left or right'