import json
import pymel.core as pm

idAttrs = {'bend': ['curvature'], 'twist': ['startAngle'], 'squash': ['factor'], 'sine': ['offset', 'highBound'],
           'flare': ['startFlareX'], 'wave': ['minRadius']}
deformerTypes = ['nonLinear']


def getNonlinearType(dfm):
    nlType = None
    for key in idAttrs.keys():
        nlType = key
        for attr in idAttrs[key]:
            if not dfm.hasAttr(attr):
                nlType = None
        if nlType:
            return nlType
    return 'Unable to determine type of nonlinear deformer: %s' % dfm.name()


def getHandle(dfm):
    handle = pm.listConnections(dfm.matrix)[0]
    return handle


def saveDeformers():
    saveFilePath = pm.fileDialog2(fileFilter='*.json')[0]
    if saveFilePath:
        saveFileDir = '/'.join(saveFilePath.split('/')[:-1]) + '/'
        dfms = [dfm for dfm in pm.ls() if pm.nodeType(dfm) in deformerTypes]
        deformerDict = {}

        for dfm in dfms:
            key = dfm.name()
            handle = getHandle(dfm)
            deformerDict[key] = {}
            deformerDict[key]['nlType'] = getNonlinearType(dfm)
            deformerDict[key]['mtx'] = pm.xform(handle, q=1, ws=1, m=1)
            deformerDict[key]['parent'] = handle.getParent().name()
            deformerDict[key]['params'] = {}
            deformerDict[key]['geo'] = [geo for geo in pm.nonLinear(dfm, q=1, geometry=1)]
            for geo in deformerDict[key]['geo']:
                fileName = '%s_%s_weights.xml' % (geo, key)
                pm.select(geo)
                pm.deformerWeights(fileName, export=1, deformer=dfm, path=saveFileDir)
            attrs = [a for a in pm.listAttr(dfm) if pm.Attribute('%s.%s' % (key, a)).isKeyable() and not 'weight' in a]
            for attr in attrs:
                deformerDict[key]['params'][attr] = pm.getAttr('%s.%s' % (dfm.name(), attr))
            deformerDict[key]['conns'] = {}
            for attr in attrs:
                if not pm.Attribute('%s.%s' % (key, attr)).isArray():
                    conn = pm.listConnections('%s.%s' % (key, attr), plugs=1, d=0)
                    if conn:
                        deformerDict[key]['conns'][attr] = conn[0].name()

        with open(saveFilePath, 'w') as outfile:
            json.dump(deformerDict, outfile)

def importDeformers(fileName):
    deformerDict = json.loads(open(fileName).read())
    fileDir = '\\'.join(fileName.split('\\')[:-1])

    for key in deformerDict.keys():
        geo = deformerDict[key]['geo']
        pm.select(geo)
        dfm = pm.nonLinear(name=key, type=deformerDict[key]['nlType'])
        pm.xform(dfm[1], ws=1, m=deformerDict[key]['mtx'])
        parent = deformerDict[key]['parent']
        if parent:
            dfm[1].setParent(parent)
        for param in deformerDict[key]['params'].keys():
            attr = pm.Attribute(('%s.%s' % (dfm[0].name(), param)))
            if not attr.isArray():
                attr.set(deformerDict[key]['params'][param])
        for conn in deformerDict[key]['conns'].keys():
            pm.Attribute(deformerDict[key]['conns'][conn]).connect('%s.%s' % (dfm[0].name(), conn))
        for g in geo:
            weightsFile = '%s_%s_weights.xml' % (g, key)

            pm.select(g)
            pm.deformerWeights(weightsFile, im=1, deformer=dfm[0], path=fileDir)

'''
TO DO:
Consider ordering of deformers on geo when rebuilding.

'''
