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

    # fk messages
    inFKStart = OpenMaya.MObject()
    inFKStartEff = OpenMaya.MObject()
    inFKMidA = OpenMaya.MObject()
    inFKMidAEff = OpenMaya.MObject()
    inFKMidB = OpenMaya.MObject()
    inFKMidBEff = OpenMaya.MObject()
    inFKEnd = OpenMaya.MObject()
    inFKEndEff = OpenMaya.MObject()

    # ik blocks
    inIKBlock = OpenMaya.MObject()
    inIKStartBlock = OpenMaya.MObject()
    inIKEndBlock = OpenMaya.MObject()
    inIKPoleBlock = OpenMaya.MObject()

    # ik messages
    inIKStart = OpenMaya.MObject()
    inIKStartEff = OpenMaya.MObject()
    inIKEnd = OpenMaya.MObject()
    inIKEndEff = OpenMaya.MObject()
    inIKPole = OpenMaya.MObject()
    inIKPoleEff = OpenMaya.MObject()

    outSwitch = OpenMaya.MObject()

    enumFK = 0
    enumIK = 1
    enumReset = 2
    fk_attributes = [
        ('.fkBlock.fkStartBlock.fkStart', ['.fkBlock.fkStartBlock.fkStartEffector', '.ikBlock.ikStartBlock.ikStart']),
        ('.fkBlock.fkMidABlock.fkMidA', ['.fkBlock.fkMidABlock.fkMidAEffector', '.ikBlock.ikMidABlock.ikMidA']),
        ('.fkBlock.fkMidBBlock.fkMidB', ['.fkBlock.fkMidBBlock.fkMidBEffector', '.ikBlock.ikMidBBlock.ikMidB']),
        ('.fkBlock.fkEndBlock.fkEnd', ['.fkBlock.fkEndBlock.fkEndEffector', '.ikBlock.ikEndBlock.ikEnd']),
    ]

    ik_attributes = [
        ('.ikBlock.ikStartBlock.ikStart', ['.ikBlock.ikStartBlock.ikStartEffector', '.fkBlock.fkStartBlock.fkStart']),
        ('.ikBlock.ikEndBlock.ikEnd', ['.ikBlock.ikEndBlock.ikEndEffector', '.fkBlock.fkEndBlock.fkEnd']),
        ('.ikBlock.ikPoleBlock.ikPole', ['.ikBlock.ikPoleBlock.ikPoleEffector']),
    ]
    reset_attributes = [
        '.fkBlock.fkStartBlock.fkStart', '.fkBlock.fkMidABlock.fkMidA', '.fkBlock.fkMidBBlock.fkMidB', '.fkBlock.fkEndBlock.fkEnd',
        '.ikBlock.ikStartBlock.ikStart', '.ikBlock.ikEndBlock.ikEnd', '.ikBlock.ikPoleBlock.ikPole'
    ]

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == ikfkSwitch.outSwitch:
            self.switchChain(dataBlock)
            
            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter
    def switchChain(self, dataBlock):
        dataHandleInSwitch = dataBlock.inputValue(ikfkSwitch.inSwitch)
        dataHandleOutSwitch = dataBlock.outputValue(ikfkSwitch.outSwitch)

        switchVal = cmds.getAttr('{}.inSwitch'.format(self.name()))
        # switchVal = dataHandleInSwitch.asInt()

        # print('switch val: {}'.format(switchVal))

        effectorList = None
        if switchVal == self.enumFK:
            effectorList = self.genFkEff()
        elif switchVal == self.enumIK:
            effectorList = self.genIKEff()
        if effectorList != None:
            print(effectorList)
            for objs in effectorList:
                cmds.matchTransform(objs[0], objs[1])

        if switchVal == self.enumReset:
            effectorList = self.genResetEff()
            if effectorList != None:
                for obj in effectorList:
                    cmds.xform(obj, t=(0, 0, 0), s=(1, 1, 1), ro=(0, 0, 0))

        dataHandleOutSwitch.setInt(switchVal)

    
    def genFkEff(self):
        fkList = []
        nodeName = self.name()
        for fk in self.fk_attributes:
            driven = cmds.listConnections('{}{}'.format(nodeName, fk[0]))
            driver = None
            if driven != None:
                for drv in fk[1]:
                    driver = cmds.listConnections('{}{}'.format(nodeName, drv))
                    if driver != None:
                        break
                if driver == None:
                    cmds.warning('no object connected to {}', fk[0,1:])
                    return None
                fkList.append((driven, driver))
        return fkList

    def genIKEff(self):
        ikList = []
        nodeName = self.name()
        for ik in self.ik_attributes:
            driven = cmds.listConnections('{}{}'.format(nodeName, ik[0]))
            driver = None
            if driven != None:
                for drv in ik[1]:
                    driver = cmds.listConnections('{}{}'.format(nodeName, drv))
                    if driver != None:
                        break
                if driver == None:
                    cmds.warning('no object connected to {}', ik[0,1:])
                    return None
                ikList.append((driven, driver))
        return ikList

    def genResetEff(self):
        resetList = []
        nodeName = self.name()
        for attr in self.reset_attributes:
            driven = cmds.listConnections('{}{}'.format(nodeName, attr))
            if driven == None:
                if attr != self.reset_attributes[1] and attr != self.reset_attributes[2]:
                    cmds.warning('no object connected to {}', attr[1:])
                    return None
            else:
                resetList.append(driven)
        return resetList

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
    mFnEnumAttr.addField('FK', ikfkSwitch.enumFK)
    mFnEnumAttr.addField('IK', ikfkSwitch.enumIK)
    mFnEnumAttr.addField('reset', ikfkSwitch.enumReset)
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

    ikfkSwitch.inFKBlock = mFnCompoundAttr.create('fkBlock', 'fkBlck')
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKStartBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidABlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKMidBBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inFKEndBlock)
    ikfkSwitch.addAttribute(ikfkSwitch.inFKBlock)

    #creating ik plugs
    ikfkSwitch.inIKStart = createMessageAttribute(mFnMessageAttr, 'ikStart', 'ikS')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKStart)
    ikfkSwitch.inIKStartEff = createMessageAttribute(mFnMessageAttr, 'ikStartEffector', 'ikSEff')
    ikfkSwitch.addAttribute(ikfkSwitch.inIKStartEff)

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
    mFnCompoundAttr.setStorable(1)
    mFnCompoundAttr.setKeyable(1)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKStartBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKEndBlock)
    mFnCompoundAttr.addChild(ikfkSwitch.inIKPoleBlock)
    ikfkSwitch.addAttribute(ikfkSwitch.inIKBlock)

    #final switch
    ikfkSwitch.outSwitch = mFnEnumAttr.create('outSwitch', 'outS')
    mFnEnumAttr.addField('FK', ikfkSwitch.enumFK)
    mFnEnumAttr.addField('IK', ikfkSwitch.enumIK)
    mFnEnumAttr.addField('reset', ikfkSwitch.enumReset)
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
        mplugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Failed to unregister command %s\n' % nodeName)