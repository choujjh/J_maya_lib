import maya.cmds as cmds

#TODO: get this stuff working

#creating an anim circle
def anim_circle(scale, rotateAngle=[0, 0, 0], center=[0, 0, 0], n='nurbsCircle', degree=3, sections=8):
    cntrl = cmds.circle(r=scale, d=degree, s=sections, ch=False, n=n, c=center)[0]
    cmds.xform(cntrl, ro=rotateAngle)
    # cmds.setAttr(cntrl+'.rotate', rotateAngle)
    cmds.makeIdentity(cntrl, apply=True, t=True, r=True, s=True, n=False, pn=True)
    return cntrl