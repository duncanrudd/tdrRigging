import pymel.core as pm

def replaceMgearMulMatrix():
    '''
    Attempts to replace all mgear mulMatrix nodes with standard maya multMatrix nodes
    :return: List of mgear mulMatrix nodes in scene 
    '''
    def _replaceConnectionName(conn, mgearNode, mayaNode):
        if conn:
            connStr = str(conn[0])
            if 'mgear' in connStr:
                connStr = connStr.replace('output', 'matrixSum')
            connStr = connStr.replace(mgearNode, mayaNode)
            connStr = connStr.replace('matrixA', 'matrixIn[0]')
            connStr = connStr.replace('matrixB', 'matrixIn[1]')
            try:
                conn = pm.Attribute(connStr)
            except:
                pass

        return conn

    mgearNodes = [node for node in pm.ls() if 'Mgear_mulMatrix' in str(type(node))]
    mgearDict = {}

    for node in mgearNodes:
        mgearDict[node.name()] = {}

        mayaNode = pm.createNode('multMatrix', name=node.name().replace('mgear', 'maya'))
        mgearDict[node.name()]['mayaNode'] = mayaNode

    for node in mgearNodes:
        mgearNode = node.name()
        mayaNode = mgearDict[node.name()]['mayaNode']
        # Matrix A
        matrixAConns = pm.listConnections(node.matrixA, p=1, c=1)
        if matrixAConns:
            if 'mgear' in str(matrixAConns[0][1]):
                mgearNode = str(matrixAConns[0][1]).split('.')[0]
            mayaNode = mgearDict[mgearNode]['mayaNode']
        matrixAConn = _replaceConnectionName(pm.listConnections(node.matrixA, p=1),
                                             mgearNode,
                                             mayaNode.name())

        # Matrix B
        matrixBConn = None
        matrixBConns = pm.listConnections(node.matrixB, p=1, c=1)
        if matrixBConns:
            if 'mgear' in str(matrixBConns[0][1]):
                mgearNode = str(matrixBConns[0][1]).split('.')[0]
            mayaNode = mgearDict[mgearNode]['mayaNode']
        matrixBConn = _replaceConnectionName(pm.listConnections(node.matrixB, p=1),
                                             mgearNode,
                                             mayaNode.name())
        if not matrixBConn:
            mtx = pm.createNode('fourByFourMatrix')
            mtxList = node.matrixB.get().tolist()
            mtx.in00.set(mtxList[0][0])
            mtx.in01.set(mtxList[0][1])
            mtx.in02.set(mtxList[0][2])

            mtx.in10.set(mtxList[1][0])
            mtx.in11.set(mtxList[1][1])
            mtx.in12.set(mtxList[1][2])

            mtx.in20.set(mtxList[2][0])
            mtx.in21.set(mtxList[2][1])
            mtx.in22.set(mtxList[2][2])

            mtx.in30.set(mtxList[3][0])
            mtx.in31.set(mtxList[3][1])
            mtx.in32.set(mtxList[3][2])

            matrixBConn = mtx.output

        # Output
        outputConns = pm.listConnections(node.output, p=1, c=1)
        outputConnsNew = []
        for i in range(len(outputConns)):

            srcCon = _replaceConnectionName([outputConns[i][0]],
                                            node.name(),
                                            mayaNode.name())
            if 'mgear' in str(outputConns[i][1]):
                mgearNode = str(outputConns[i][1]).split('.')[0]
                mayaNode = mgearDict[mgearNode]['mayaNode']
            destCon = _replaceConnectionName([outputConns[i][1]],
                                             mgearNode,
                                             mayaNode.name())
            outputConnsNew.append(destCon)

        mgearDict[node.name()]['matrixAConn'] = matrixAConn
        mgearDict[node.name()]['matrixBConn'] = matrixBConn
        mgearDict[node.name()]['outputConn'] = outputConnsNew

    for key in mgearDict.keys():
        mayaNode = mgearDict[key]['mayaNode']
        if mgearDict[key]['matrixAConn']:
            print 'attempt matrixA'
            try:
                mgearDict[key]['matrixAConn'].connect(mayaNode.matrixIn[0])
            except:
                pass
        if mgearDict[key]['matrixBConn']:
            print 'attempt matrixB'
            try:
                mgearDict[key]['matrixBConn'].connect(mayaNode.matrixIn[1])
            except:
                pass
        if mgearDict[key]['outputConn']:
            for conn in mgearDict[key]['outputConn']:
                try:
                    mayaNode.matrixSum.connect(conn, f=1)
                except:
                    pass

    return mgearNodes