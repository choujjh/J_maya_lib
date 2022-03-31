import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmdschainLength
import math as math

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
            dataHandleInCntrlDist = dataBlock.inputValue(ikfkSwitch.inControlDistance)
            dataHandleInSoft = dataBlock.inputValue(ikfkSwitch.inSoft)
            dataHandleInChainLen = dataBlock.inputValue(ikfkSwitch.inChainLength)

            cntrlDist  = dataHandleInCntrlDist.asFloat()
            soft = dataHandleInSoft.asFloat()
            chainLen = dataHandleInChainLen.asFloat()
            softDist = cntrlDist

            if(cntrlDist > chainLen-soft):
                if soft > 0:
                    soft = chainLen - soft * math.pow(math.e, (-(cntrlDist-(chainLen-soft))/soft))
                else:
                    softDist = chainLen

            dataHandleOutSwitch = dataBlock.outputValue(ikfkSwitch.outSoftDistance)
            dataHandleOutSwitch.setFloat(softDist)
            
            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(softIKDistance())
def nodeInitializer():
    # 1. create a function set
    mFnNumericAttribute = OpenMaya.MFnNumericAttribute()

    # 2. create the attributes
    softIKDistance.inControlDistance = mFnNumericAttribute.create('controlDistance', 'cntrlDist', 'kFloat', 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(1)
    mFnNumericAttribute.setStorable(1)
    mFnNumericAttribute.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inControlDistance)

    softIKDistance.inSoft = mFnNumericAttribute.create('soft', 's', 'kFloat', 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(1)
    mFnNumericAttribute.setStorable(1)
    mFnNumericAttribute.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inSoft)

    softIKDistance.inChainLength = mFnNumericAttribute.create('chainLength', 'chainLen', 'kFloat', 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(1)
    mFnNumericAttribute.setStorable(1)
    mFnNumericAttribute.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inChainLength)

    softIKDistance.outSoftDistance = mFnNumericAttribute.create('softDistance', 'softDist', 'kFloat', 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(0)
    mFnNumericAttribute.setStorable(0)
    mFnNumericAttribute.setKeyable(0)
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