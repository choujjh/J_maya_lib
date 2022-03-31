import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

nodeName = 'softIKDistance'
nodeId = OpenMaya.MTypeId(0x111112)

class softIKDistance(OpenMayaMPx.MPxNode):

    # fk blocks
    inControlDistance = OpenMaya.MObject()
    inSoft = OpenMaya.MObject()
    inChainLength = OpenMaya.MObject()

    outSoftDistance = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == softIKDistance.outSoftDistance:
            mFnMessageAttr = OpenMaya.MFnMessageAttribute()
            mFnCompoundAttr = OpenMaya.MFnCompoundAttribute()
            
            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter

        
    def switchChain(self, dataBlock):
        dataHandleInSwitch = dataBlock.inputValue(ikfkSwitch.inSwitch)
        dataHandleOutSwitch = dataBlock.outputValue(ikfkSwitch.outSwitch)

        switchVal = cmds.getAttr('{}.inSwitch'.format(self.name()))

        dataHandleOutSwitch.setInt(switchVal)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(softIKDistance())
def nodeInitializer():
    # 1. create a function set
    mFnNumericAttribute = OpenMaya.MFnNumericAttribute()

    # 2. create the attributes
    softIKDistance.inControlDistance = mFnEnumAttr.create('controlDistance', 'cntrlDist', 'kFloat', 0)
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(1)
    mFnEnumAttr.setStorable(1)
    mFnEnumAttr.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inControlDistance)

    softIKDistance.inSoft = mFnEnumAttr.create('soft', 's', 'kFloat', 0)
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(1)
    mFnEnumAttr.setStorable(1)
    mFnEnumAttr.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inSoft)

    softIKDistance.inChainLength = mFnEnumAttr.create('chainLength', 'chainLen', 'kFloat', 0)
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(1)
    mFnEnumAttr.setStorable(1)
    mFnEnumAttr.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inChainLength)

    softIKDistance.outSoftDistance = mFnEnumAttr.create('softDistance', 'softDist', 'kFloat', 0)
    mFnEnumAttr.setReadable(1)
    mFnEnumAttr.setWritable(0)
    mFnEnumAttr.setStorable(0)
    mFnEnumAttr.setKeyable(0)
    softIKDistance.addAttribute(softIKDistance.outSoftDistance)

    # 4. designing circuitry
    softIKDistance.attributeAffects(softIKDistance.inControlDistance, softIKDistance.outSoftDistance)
    softIKDistance.attributeAffects(softIKDistance.inSoft, softIKDistance.outSoftDistance)
    softIKDistance.attributeAffects(softIKDistance.inChainLength, softIKDistance.outSoftDistance)

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