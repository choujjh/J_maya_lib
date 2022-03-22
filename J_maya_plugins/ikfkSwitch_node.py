import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

nodeName = 'ikfkSwitch'
nodeId = OpenMaya.MTypeId(0x111111)

class ikfkSwitch(OpenMayaMPx.MPxNode):

    inSwitch = OpenMaya.MObject()

    inFKStart = OpenMaya.MObject()
    inFKMidA = OpenMaya.MObject()
    inFKMidB = OpenMaya.MObject()
    inFKEnd = OpenMaya.MObject()
    inFKPole = OpenMaya.MObject()

    inIKStart = OpenMaya.MObject()
    inIKMidA = OpenMaya.MObject()
    inIKMidB = OpenMaya.MObject()
    inIKEnd = OpenMaya.MObject()
    inIKPole = OpenMaya.MObject()

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
        switchVal = dataHandleInSwitch.asInt()

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
            if switchVal == 0:
                print('to fk')
                cmds.matchTransform(start['fk'], start['ik'])
                if midA['fk'] != None and midA['ik'] != None:
                    cmds.matchTransform(midA['fk'], midA['ik'])
                if midB['fk'] != None and midB['ik'] != None:
                    cmds.matchTransform(midB['fk'], midB['ik'])
                cmds.matchTransform(end['fk'], end['ik'])
            # ik
            elif switchVal == 1:
                print('to ik')
                cmds.matchTransform(start['ik'], start['fk'])
                cmds.matchTransform(end['ik'], end['fk'])
                cmds.matchTransform(pole['ik'], pole['fk'])
            # reset
            elif switchVal == 2:
                print('reset')
                resetList = [start['ik'], start['fk'], 
                            midA['fk'], midB['fk'],
                            end['ik'], end['fk'], 
                            pole['ik']]
                for obj in resetList:
                    if obj != None:
                        cmds.xform(obj, t=(0, 0, 0), s=(1, 1, 1), ro=(0, 0, 0))

        dataHandleOutSwitch.setInt(switchVal)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(ikfkSwitch())

def nodeInitializer():
    # 1. create a function set
    mFnEnumAttr = OpenMaya.MFnEnumAttribute()
    mFnMessageAttr = OpenMaya.MFnMessageAttribute()

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

    ikfkSwitch.inFKStart =  mFnMessageAttr.create('fkStart', 'fkS')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)

    ikfkSwitch.inFKMidA =  mFnMessageAttr.create('fkMidA', 'fkMA')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inFKMidB =  mFnMessageAttr.create('fkMidB', 'fkMB')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inFKEnd =  mFnMessageAttr.create('fkEnd', 'fkE')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inFKPole =  mFnMessageAttr.create('fkPole', 'fkP')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)

    ikfkSwitch.inIKStart =  mFnMessageAttr.create('ikStart', 'ikS')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inIKMidA =  mFnMessageAttr.create('ikMidA', 'ikMA')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inIKMidB =  mFnMessageAttr.create('ikMidB', 'ikMB')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inIKEnd =  mFnMessageAttr.create('ikEnd', 'ikE')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)
    ikfkSwitch.inIKPole =  mFnMessageAttr.create('ikPole', 'ikP')
    mFnMessageAttr.setReadable(1)
    mFnMessageAttr.setWritable(1)
    mFnMessageAttr.setStorable(1)
    mFnMessageAttr.setKeyable(1)

    ikfkSwitch.outSwitch = mFnEnumAttr.create('outSwitch', 'outS')
    mFnEnumAttr.addField('FK', 0)
    mFnEnumAttr.addField('IK', 1)
    mFnEnumAttr.addField('reset', 2)
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(0)
    mFnEnumAttr.setStorable(0)
    mFnEnumAttr.setKeyable(0)

    # 3. attaching the attributes to the Node
    ikfkSwitch.addAttribute(ikfkSwitch.inSwitch)

    ikfkSwitch.addAttribute(ikfkSwitch.inFKStart)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidA)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKMidB)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKEnd)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKPole)

    ikfkSwitch.addAttribute(ikfkSwitch.inIKStart)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidA)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKMidB)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKEnd)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKPole)

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
        mplugin.deregisterNode(nodeName, nodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to unregister command %s\n' % nodeName)