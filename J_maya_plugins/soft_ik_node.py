import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
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
            dataHandleInCntrlDist = dataBlock.inputValue(softIKDistance.inControlDistance)
            dataHandleInSoft = dataBlock.inputValue(softIKDistance.inSoft)
            dataHandleInChainLen = dataBlock.inputValue(softIKDistance.inChainLength)
            dataHandleOutSwitch = dataBlock.outputValue(softIKDistance.outSoftDistance)

            cntrlDist  = dataHandleInCntrlDist.asFloat()
            soft = dataHandleInSoft.asFloat()
            chainLen = dataHandleInChainLen.asFloat()
            softDist = cntrlDist

            if(cntrlDist > chainLen-soft):
                # print('first cntrl')
                if soft > 0:
                    # print('soft > 0')
                    softDist = chainLen - soft * math.pow(math.e, (-(cntrlDist-(chainLen-soft))/soft))
                else:
                    # print('chain Len')
                    softDist = chainLen

            
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
    softIKDistance.inControlDistance = mFnNumericAttribute.create('controlDistance', 'cntrlDist', OpenMaya.MFnNumericData.kFloat, 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(1)
    mFnNumericAttribute.setStorable(1)
    mFnNumericAttribute.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inControlDistance)

    softIKDistance.inSoft = mFnNumericAttribute.create('soft', 's', OpenMaya.MFnNumericData.kFloat, 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(1)
    mFnNumericAttribute.setStorable(1)
    mFnNumericAttribute.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inSoft)

    softIKDistance.inChainLength = mFnNumericAttribute.create('chainLength', 'chainLen', OpenMaya.MFnNumericData.kFloat, 0)
    mFnNumericAttribute.setReadable(1)
    mFnNumericAttribute.setWritable(1)
    mFnNumericAttribute.setStorable(1)
    mFnNumericAttribute.setKeyable(1)
    softIKDistance.addAttribute(softIKDistance.inChainLength)

    softIKDistance.outSoftDistance = mFnNumericAttribute.create('softDistance', 'softDist', OpenMaya.MFnNumericData.kFloat, 0)
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
        return mplugin.deregisterNode(nodeId)
    except:
        sys.stderr.write('Failed to unregister command %s\n' % nodeName)    