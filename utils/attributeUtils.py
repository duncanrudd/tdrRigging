def attrCtrl(lock=True, keyable=False, channelBox=False, nodeList=[], attrList=[]):
    '''
    Takes a list of nodes and sets locks/unlocks shows/hides attributes in attrList
    '''
    if nodeList:
        for node in nodeList:
            if attrList:
                for a in attrList:
                    if node.hasAttr(a):
                        pmc.setAttr('%s.%s' % (node, a), lock=lock, keyable=keyable, channelBox=channelBox)
            else:
                return 'attrCtrl: No nodes supplied for attribute control'
    else:
        return 'attrCtrl: No nodes supplied for attribute control'