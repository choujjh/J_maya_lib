import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

nodeName = 'ikfkSwitch'
nodeId = OpenMaya.MTypeId(0x111111)

class ikfkSwitch(OpenMayaMPx.MPxNode):

    inSwitch = OpenMaya.MObject()

    # fk blocks
    inFKBlock = OpenMaya.MObject()
    inFKStartBlock = OpenMaya.MObject()
    inFKMidABlock = OpenMaya.MObject()
    inFKMidBBlock = OpenMaya.MObject()
    inFKEndBlock = OpenMaya.MObject()
    inFKPoleBlock = OpenMaya.MObject()

    # fk messages
    inFKStart = OpenMaya.MObject()
    inFKStartEff = OpenMaya.MObject()
    inFKMidA = OpenMaya.MObject()
    inFKMidAEff = OpenMaya.MObject()
    inFKMidB = OpenMaya.MObject()
    inFKMidBEff = OpenMaya.MObject()
    inFKEnd = OpenMaya.MObject()
    inFKEndEff = OpenMaya.MObject()
    inFKPole = OpenMaya.MObject()
    inFKPoleEff = OpenMaya.MObject()

    # ik blocks
    inIKBlock = OpenMaya.MObject()
    inIKStartBlock = OpenMaya.MObject()
    inIKMidABlock = OpenMaya.MObject()
    inIKMidBBlock = OpenMaya.MObject()
    inIKEndBlock = OpenMaya.MObject()
    inIKPoleBlock = OpenMaya.MObject()

    # ik messages
    inIKStart = OpenMaya.MObject()
    inIKStartEff = OpenMaya.MObject()
    inIKMidA = OpenMaya.MObject()
    inIKMidAEff = OpenMaya.MObject()
    inIKMidB = OpenMaya.MObject()
    inIKMidBEff = OpenMaya.MObject()
    inIKEnd = OpenMaya.MObject()
    inIKEndEff = OpenMaya.MObject()
    inIKPole = OpenMaya.MObject()
    inIKPoleEff = OpenMaya.MObject()

    outSwitch = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == ikfkSwitch.outSwitch:
            self.switchChain(dataBlock)
            
            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter
    def switchChain(self, dataBlock):
        ikfkSwitchNode = self.name()
        dataHandleInSwitch = dataBlock.inputValue(ikfkSwitch.inSwitch)
        dataHandleOutSwitch = dataBlock.outputValue(ikfkSwitch.outSwitch)
        switchVal = cmds.getAttr(ikfkSwitchNode + '.inSwitch') #dataHandleInSwitch.asInt()

        start = {'fk':cmds.listConnections('{}.fkStart'.format(ikfkSwitchNode)), 
                'ik':cmds.listConnections('{}.ikStart'.format(ikfkSwitchNode))}
        midA = {'fk':cmds.listConnections('{}.fkMidA'.format(ikfkSwitchNode)), 
                'ik':cmds.listConnections('{}.ikMidA'.format(ikfkSwitchNode))}
        midB = {'fk':cmds.listConnections('{}.fkMidB'.format(ikfkSwitchNode)), 
                'ik':cmds.listConnections('{}.ikMidB'.format(ikfkSwitchNode))}
        end = {'fk':cmds.listConnections('{}.fkEnd'.format(ikfkSwitchNode)), 
                'ik':cmds.listConnections('{}.ikEnd'.format(ikfkSwitchNode))}
        pole = {'fk':cmds.listConnections('{}.fkPole'.format(ikfkSwitchNode)), 
                'ik':cmds.listConnections('{}.ikPole'.format(ikfkSwitchNode))}
        hasWarning = False
        if start['ik'] == None or start['fk'] == None:
            cmds.warning('{} start fk/ik doesn\'t have connections'.format(ikfkSwitchNode))
            hasWarning = True
        elif end['ik'] == None or end['fk'] == None:
            cmds.warning('{} end fk/ik doesn\'t have connections'.format(ikfkSwitchNode))
            hasWarning = True
        elif pole['ik'] == None or pole['fk'] == None:
            cmds.warning('{} pole fk/ik doesn\'t have connections'.format(ikfkSwitchNode))
            hasWarning = True
        
        if not hasWarning:
            # fk
            print('switch:', switchVal)
            if switchVal == 0:
                cmds.matchTransform(start['fk'], start['ik'])
                if midA['fk'] != None and midA['ik'] != None:
                    cmds.matchTransform(midA['fk'], midA['ik'])
                if midB['fk'] != None and midB['ik'] != None:
                    cmds.matchTransform(midB['fk'], midB['ik'])
                cmds.matchTransform(end['fk'], end['ik'])
                # dataHandleOutSwitch.setInt(switchVal)
            # ik
            elif switchVal == 1:
                cmds.matchTransform(start['ik'], start['fk'])
                cmds.matchTransform(end['ik'], end['fk'])
                cmds.matchTransform(pole['ik'], pole['fk'])
                # dataHandleOutSwitch.setInt(switchVal)
            # reset
            elif switchVal == 2:
                resetList = [start['ik'], start['fk'], 
                            midA['fk'], midB['fk'],
                            end['ik'], end['fk'], 
                            pole['ik']]
                for obj in resetList:
                    if obj != None:
                        cmds.xform(obj, t=(0, 0, 0), s=(1, 1, 1), ro=(0, 0, 0))
                # dataHandleInSwitch.setInt(0)
            dataHandleOutSwitch.setInt(switchVal)

        # dataHandleOutSwitch.setInt(switchVal)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ikfkSwitch())

def createMessageAttribute(mFnMessageAttr, longName, shortName):
    saveTo =  mFnMessageAttr.create(longName, shortName)
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    return saveTo
def nodeInitializer():
    # 1. create a function set
    mFnEnumAttr = OpenMaya.MFnEnumAttribute()
    mFnMessageAttr = OpenMaya.MFnMessageAttribute()
    mFnCompoundAttr = OpenMaya.MFnCompoundAttribute()

    # 2. create the attributes
    ikfkSwitch.inSwitch = mFnEnumAttr.create('inSwitch', 'inS')
    mFnEnumAttr.addField('FK', 0)
    mFnEnumAttr.addField('IK', 1)
    mFnEnumAttr.addField('reset', 2)
    mFnEnumAttr.default = 0
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(1)
    mFnEnumAttr.setStorable(1)
    mFnEnumAttr.setKeyable(1)
    ikfkSwitch.addAttribute(ikfkSwitch.inSwitch)

    #creating fk plugs
    ikfkSwitch.inFKStart = createMessageAttribute(mFnMessageAttr, 'fkStart', 'fkS')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKStart)
    ikfkSwitch.inFKStartEff = createMessageAttribute(mFnMessageAttr, 'fkStartEffector', 'fkSEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKStartEff)


    ikfkSwitch.inFKMidA = createMessageAttribute(mFnMessageAttr, 'fkMidA', 'fkMA')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidA)
    ikfkSwitch.inFKMidAEff = createMessageAttribute(mFnMessageAttr, 'fkMidAEffector', 'fkMAEFF')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidAEff)

    ikfkSwitch.inFKMidB = createMessageAttribute(mFnMessageAttr, 'fkMidB', 'fkMB')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidB)
    ikfkSwitch.inFKMidBEff = createMessageAttribute(mFnMessageAttr, 'fkMidBEffector', 'fkMBEFF')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidBEff)

    ikfkSwitch.inFKEnd = createMessageAttribute(mFnMessageAttr, 'fkEnd', 'fkE')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKEnd)
    ikfkSwitch.inFKEndEff = createMessageAttribute(mFnMessageAttr, 'fkEndEffector', 'fkEEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKEndEff)

    ikfkSwitch.inFKPole = createMessageAttribute(mFnMessageAttr, 'fkPole', 'fkP')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKPole)
    ikfkSwitch.inFKPoleEff = createMessageAttribute(mFnMessageAttr, 'fkPoleEffector', 'fkPEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inFKPoleEff)

    #creating fk blocks
    ikfkSwitch.inFKStartBlock = mFnCompoundAttr.create('fkStartBlock', 'fkStartBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKStart)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKStartEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKStartBlock)

    ikfkSwitch.inFKMidABlock = mFnCompoundAttr.create('fkMidABlock', 'fkMidABlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidA)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidAEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidABlock)

    ikfkSwitch.inFKMidBBlock = mFnCompoundAttr.create('fkMidBBlock', 'fkMidBBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidB)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidBEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidBBlock)
    
    ikfkSwitch.inFKEndBlock = mFnCompoundAttr.create('fkEndBlock', 'fkEndBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKEnd)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKEndEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKEndBlock)

    ikfkSwitch.inFKPoleBlock = mFnCompoundAttr.create('fkPoleBlock', 'fkPoleBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKPole)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKPoleEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKPoleBlock)

    ikfkSwitch.inFKBlock = mFnCompoundAttr.create('fkBlock', 'fkBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKStartBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidABlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidBBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKEndBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKPoleBlock)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKBlock)

    #creating ik plugs
    ikfkSwitch.inIKStart = createMessageAttribute(mFnMessageAttr, 'ikStart', 'ikS')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKStart)
    ikfkSwitch.inIKStartEff = createMessageAttribute(mFnMessageAttr, 'ikStartEffector', 'ikSEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKStartEff)

    ikfkSwitch.inIKMidA = createMessageAttribute(mFnMessageAttr, 'ikMidA', 'ikMA')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidA)
    ikfkSwitch.inIKMidAEff = createMessageAttribute(mFnMessageAttr, 'ikMidAEffector', 'ikMAEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidAEff)

    ikfkSwitch.inIKMidB = createMessageAttribute(mFnMessageAttr, 'ikMidB', 'ikMB')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidB)
    ikfkSwitch.inIKMidBEff = createMessageAttribute(mFnMessageAttr, 'ikMidBEffector', 'ikMBEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidBEff)

    ikfkSwitch.inIKEnd = createMessageAttribute(mFnMessageAttr, 'ikEnd', 'ikE')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKEnd)
    ikfkSwitch.inIKEndEff = createMessageAttribute(mFnMessageAttr, 'ikEndEffector', 'ikEEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKEndEff)

    ikfkSwitch.inIKPole = createMessageAttribute(mFnMessageAttr, 'ikPole', 'ikP')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKPole)
    ikfkSwitch.inIKPoleEff = createMessageAttribute(mFnMessageAttr, 'ikPoleEffector', 'ikPEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKPoleEff)

    #creating ik blocks
    ikfkSwitch.inIKStartBlock = mFnCompoundAttr.create('ikStartBlock', 'ikStartBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKStart)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKStartEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKStartBlock)

    ikfkSwitch.inIKMidABlock = mFnCompoundAttr.create('ikMidABlock', 'ikMidABlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKMidA)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKMidAEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidABlock)

    ikfkSwitch.inIKMidBBlock = mFnCompoundAttr.create('ikMidBBlock', 'ikMidBBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKMidB)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKMidBEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidBBlock)

    ikfkSwitch.inIKEndBlock = mFnCompoundAttr.create('ikEndBlock', 'ikEndBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKEnd)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKEndEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKEndBlock)

    ikfkSwitch.inIKPoleBlock = mFnCompoundAttr.create('ikPoleBlock', 'ikPoleBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKPole)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKPoleEff)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKPoleBlock)

    ikfkSwitch.inIKBlock = mFnCompoundAttr.create('ikBlock', 'ikBlck')
    # mFnCompoundAttr.setStorable(1)
    # mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKStartBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKMidABlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKMidBBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKEndBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKPoleBlock)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKBlock)

    #final switch
    ikfkSwitch.outSwitch = mFnEnumAttr.create('outSwitch', 'outS')
    mFnEnumAttr.addField('FK', 0)
    mFnEnumAttr.addField('IK', 1)
    mFnEnumAttr.addField('reset', 2)
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(0)
    mFnEnumAttr.setStorable(0)
    mFnEnumAttr.setKeyable(0)
    ikfkSwitch.addAttribute(ikfkSwitch.outSwitch)

    # 4. designing circuitry
    ikfkSwitch.attributeAffects(ikfkSwitch.inSwitch, ikfkSwitch.outSwitch)

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to register command %s\n' % nodeName)

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeName, nodeId)
    except:
        sys.stderr.write('Failed to unregister command %s\n' % nodeName)