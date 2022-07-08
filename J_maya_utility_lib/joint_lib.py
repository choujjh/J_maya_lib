import maya.cmds as cmds
from J_maya_lib.J_maya_utility_lib import utility_helpers, object_lib, anim_controls, utility_data
'''
TODO:
stretchy IK
twist extraction
volume preservation
'''

class joint_info:
    def __init__(self, color=5, radius=0.5):
        self.color = color
        self.radius = radius
def set_radius(joints, radius):
    joints = utility_helpers.turn_to_list(joints)
    for j in joints:
        if cmds.nodeType(j) == 'joint':
            cmds.setAttr('{}.radius'.format(j), radius)

def create_ind_ik_handles(joints, pre = '', post = 'Handle', custom = ('', ''), rot_plane_slv=True):
    # get the hierarchy
    joints = utility_helpers.turn_to_list(joints)
    cmds.select(joints)
    cmds.select(hi=True)
    joints = object_lib.filter_node_types(cmds.ls(sl=True, long=True), 'joint', remove=False)
    joint_dict = {}

    # get every joint and its parent
    for j in joints:
        parent, child = utility_helpers.split_obj_name(j)[0], j
        if parent in joint_dict.keys():
            joint_dict[parent].append(child)
        else:
            joint_dict[parent] = [child]

    # remove everything that has more than 1 child and is not a joint
    for j in list(joint_dict.keys()):
        if len(joint_dict[j]) > 1:
            del joint_dict[j]
        elif cmds.objExists(j) == False:
            del joint_dict[j]
        elif cmds.nodeType(j) != 'joint' or cmds.nodeType(joint_dict[j]) != 'joint':
            del joint_dict[j]
    ik_handles = []

    #create ik handles for each pair
    for j in joint_dict.keys():
        handle = utility_helpers.split_obj_name(j)
        handle = utility_helpers.string_manip(handle[1], pre = pre, post = post, custom = custom)
        if rot_plane_slv:
            ik_handles.append(cmds.ikHandle( n = handle, sj = j, ee = joint_dict[j][0], sol = 'ikRPsolver')[0])
        else:
            ik_handles.append(cmds.ikHandle(n = handle, sj = j, ee = joint_dict[j][0], sol = 'ikSCsolver')[0])
    return ik_handles

def setup_ik_chain(ik_start_jnt, ik_end_jnt, ik_name, color=None):
    ik_name = utility_helpers.string_manip(ik_name, post='_ik')
    #ik joint chain
    handle, effector = cmds.ikHandle( n = utility_helpers.string_manip(ik_name, post = 'handle'), sj = ik_start_jnt, ee = ik_end_jnt, sol = 'ikRPsolver')
    cmds.setAttr('{}.visibility'.format(handle), False)
    effector = cmds.rename(effector, utility_helpers.string_manip(ik_name, post = 'eff'))
    #create offset grps
    loc_start = cmds.spaceLocator(n = utility_helpers.string_manip(ik_name, pre = 'anim', post = 'locOffset'))[0]
    loc_handle = cmds.spaceLocator(n = utility_helpers.string_manip(ik_name, pre = 'anim', post = 'handle_locOffset'))[0]
    for obj in [loc_start, loc_handle]:
        cmds.setAttr('{}.visibility'.format(obj), False)
    #matching transforms
    cmds.matchTransform(loc_start, ik_start_jnt)
    cmds.matchTransform(loc_handle, ik_end_jnt)
    #attach everything
    cmds.pointConstraint(loc_start, ik_start_jnt)
    cmds.pointConstraint(loc_handle, handle)
    cmds.orientConstraint(loc_handle, ik_end_jnt)
    ik_grp = cmds.createNode('transform', n=utility_helpers.string_manip(ik_name, post = 'grp01'))
    

    #attach controls
    #end
    anim_end = anim_controls.anim_circle(1, rotateAngle=[0,90,90], center=[0, -1, 0], n=utility_helpers.string_manip(ik_name, pre = 'anim', post = 'end'), degree=1, sections=3)
    dist = get_chain_len(ik_start_jnt, ik_end_jnt)
    attr_list = [utility_data.JObject_attr_info('stretch', 'bool', True),
        utility_data.JObject_attr_info('soft_perc', 'float', 1, min=0, max=1),
        utility_data.JObject_attr_info('ik_len', 'float', 0)]
    object_lib.add_attributes(anim_end, attr_list, 'IK_Attr')
    cmds.setAttr('{}.ik_len'.format(anim_end), dist)
    
    cmds.matchTransform(anim_end, ik_end_jnt)
    cmds.parent(loc_handle, anim_end)
    cmds.parent(object_lib.create_parent_grp(anim_end)[0], ik_grp)

    #start
    anim_start = anim_controls.anim_circle(1, rotateAngle=[0,0,180], center=[0, -1, 0], n=utility_helpers.string_manip(ik_start_jnt, pre = 'anim'), degree=1, sections=3)
    cmds.matchTransform(anim_start, ik_start_jnt)
    cmds.parent(loc_start, anim_start)
    cmds.parent(object_lib.create_parent_grp(anim_start)[0], ik_grp)

    #get the pole value
    pole_grp, ik_pole = cmds.parent(setup_pole_vec(ik_start_jnt, ik_end_jnt, ik_name, handle), ik_grp)
    if color != None:
        object_lib.color_object(ik_grp, color, hierarchy=True)

    #lock len attr
    cmds.setAttr('{}.ik_len'.format(anim_end), lock=True)

    return ik_grp, ik_pole
def get_chain_len(start_jnt, end_jnt):
    long = cmds.ls(end_jnt, long=True)[0]
    index = long.find(utility_helpers.split_obj_name(start_jnt)[1])
    long = long[index:].split('|')
    dist = 0
    for i in range(len(long) - 1):
        firstPoint = utility_data.JVector(cmds.xform(long[i], q=True, piv=True, ws=True)[:3])
        secondPoint = utility_data.JVector(cmds.xform(long[i+1], q=True, piv=True, ws=True)[:3])
        firstPoint = secondPoint-firstPoint
        mag = firstPoint.mag()
        dist = dist+mag
    return dist

def stretchy_ik(ik_start_jnt, ik_name, end_control):
    #cond = cmds.createNode('condition', n = '{}_stretch_cond'.format(ik_name))
    print("stretchy")

def setup_pole_vec(ik_start_jnt, ik_end_jnt, ik_name, handle):
    #objects
    ik_mid_jnt = cmds.listRelatives(ik_start_jnt, c=True)[0]
    loc_pole_vec = cmds.spaceLocator(n = utility_helpers.string_manip(ik_name, pre = 'anim', post = 'poleVec_locOffset'))[0]
    cmds.setAttr('{}.visibility'.format(loc_pole_vec), False)
    anim_obj = anim_controls.anim_circle(1, rotateAngle=[0,0,0], center=[0, 0.5, 0], n=utility_helpers.string_manip(ik_name, pre = 'anim', post = 'poleVec'), degree=1, sections=3)

    current_pole_vec = utility_data.JVector([cmds.getAttr('{}.poleVectorX'.format(handle)), cmds.getAttr('{}.poleVectorY'.format(handle)), cmds.getAttr('{}.poleVectorZ'.format(handle))])
    #create a group above and constrain it to the start
    temp_grp = object_lib.create_parent_grp(loc_pole_vec, post='temp')[0]
    start_pointC = cmds.pointConstraint(ik_start_jnt, temp_grp)
    cmds.delete(start_pointC)
    #move loc to have pull values
    cmds.move(current_pole_vec.values[0], current_pole_vec.values[1], current_pole_vec.values[2], loc_pole_vec, os=True)
    cmds.parent(loc_pole_vec, w=True)
    #aiming the group
    start_aimC = cmds.aimConstraint(ik_end_jnt, temp_grp, weight=1, worldUpType="object", worldUpObject=loc_pole_vec)
    cmds.delete(start_aimC)
    cmds.parent(loc_pole_vec, temp_grp)
    cmds.rotate(0, 0, 0, loc_pole_vec)
    #constraining locator to be more centered
    loc_pointC = cmds.pointConstraint(ik_mid_jnt, loc_pole_vec, skip=['y', 'z'])
    #offsetting control
    cmds.setAttr('{}.translateY'.format(loc_pole_vec), get_chain_len(ik_start_jnt, ik_end_jnt) * 0.4)
    cmds.delete(loc_pointC)
    cmds.matchTransform(anim_obj, loc_pole_vec)
    cmds.parent(loc_pole_vec, anim_obj)
    cmds.delete(temp_grp)

    
    #create an offset grp
    pole_grp=object_lib.create_parent_grp(anim_obj)[0]
    cmds.poleVectorConstraint(loc_pole_vec, handle)

    #create annotate
    make_annotation(ik_mid_jnt, anim_obj, ik_name)

    return pole_grp, anim_obj
def make_annotation(point_to, point_from, name):
    ann_point = cmds.spaceLocator(n = '{}_ann_point'.format(name))[0]
    cmds.setAttr('{}.visibility'.format(ann_point), False)
    cmds.parent(ann_point, point_to)
    cmds.makeIdentity(ann_point)

    ann = cmds.annotate(ann_point, tx=name)
    ann = cmds.listRelatives(ann, p=True)[0]
    ann = cmds.rename(ann, name + '_ann')
    cmds.parent(ann, point_from)
    cmds.makeIdentity(ann)

#add an ik naming convention
def setup_jnt_chain(start_jnt, end_jnt, name, switch_cntrl, ik_info, fk_info, jnt_info, ik_cntrl_color, fk_cntrl_color):

    node_editor_nodes = []
    utility_helpers.select_obj_hierarchy(start_jnt)
    set_radius(cmds.ls(sl=True, long=True), jnt_info.radius)

    #ik joints
    ik_start_jnt = object_lib.dupl_renamer(start_jnt, post = 'ik')[0]
    utility_helpers.select_obj_hierarchy(ik_start_jnt)
    set_radius(cmds.ls(sl=True, long=True), ik_info.radius)
    ik_end_jnt = utility_helpers.string_manip(end_jnt, post = 'ik')
    #delete child after end joints
    if cmds.listRelatives(ik_end_jnt, c=True) != None:
        cmds.delete(cmds.listRelatives(ik_end_jnt, c=True))
    object_lib.color_object(ik_start_jnt, ik_info.color, hierarchy=True)
    
    #fk joints
    fk_start_jnt = object_lib.dupl_renamer(start_jnt, post = 'fk')[0]
    fk_end_jnt = utility_helpers.string_manip(end_jnt, post = 'fk')
    utility_helpers.select_obj_hierarchy(fk_start_jnt)
    set_radius(cmds.ls(sl=True, long=True), fk_info.radius)
    #delete child after end joints
    if cmds.listRelatives(fk_end_jnt, c=True) != None:
        cmds.delete(cmds.listRelatives(fk_end_jnt, c=True))
    object_lib.color_object(fk_start_jnt, fk_info.color, hierarchy=True)

    #setup
    ik_grp, ik_pole = setup_ik_chain(ik_start_jnt, ik_end_jnt, name, color=ik_cntrl_color)
    fk_grp = object_lib.create_fk_cntrl(fk_start_jnt, color=fk_cntrl_color)
    object_lib.color_object(start_jnt, jnt_info.color, hierarchy=True)

    #connecting them together
    attr_list = [utility_data.JObject_attr_info('blend', 'float', default=0, min=0, max=1)]
    object_lib.add_attributes(switch_cntrl, attr_list, 'IK_to_FK')

    attr_list = [utility_data.JObject_attr_info('world_scale', 'float', default=1, min=0)]
    object_lib.add_attributes(switch_cntrl, attr_list, None)
    
    long = cmds.ls(end_jnt, long=True)[0]
    index = long.find(utility_helpers.split_obj_name(start_jnt)[1])
    long = long[index:].split('|')
    for obj in long:
        curr_ik_jnt = utility_helpers.string_manip(obj, post = 'ik')
        curr_fk_jnt = utility_helpers.string_manip(obj, post = 'fk')
        for attr in ['translate', 'rotate', 'scale']:
            bc = cmds.createNode('blendColors', n = '{}_{}_blendColor'.format(obj, attr))
            node_editor_nodes.append(bc)
            cmds.connectAttr('{}.blend'.format(switch_cntrl), '{}.blender'.format(bc))
            cmds.connectAttr('{}.{}'.format(curr_fk_jnt, attr), '{}.color1'.format(bc))
            cmds.connectAttr('{}.{}'.format(curr_ik_jnt, attr), '{}.color2'.format(bc))
            cmds.connectAttr('{}.output'.format(bc), '{}.{}'.format(obj, attr))
    
    cmds.sets(node_editor_nodes, n=name + '_set')

    #new stuff that need to refactor eventually

    cmds.addAttr(switch_cntrl, ln = 'mode', at='enum', en = "FK:IK:reset:")
    cmds.setAttr('{}.mode'.format(switch_cntrl), e=True, keyable=True)

    cmds.connectAttr('{}.blend'.format(switch_cntrl), '{}.visibility'.format(fk_grp[0]))
    reverse = cmds.createNode('reverse', n = utility_helpers.string_manip(name, post = 'ik_reverse'))
    cmds.connectAttr('{}.blend'.format(switch_cntrl), '{}.inputX'.format(reverse))
    cmds.connectAttr('{}.outputX'.format(reverse), '{}.visibility'.format(ik_grp))

    print(ik_pole)
    fk_aim = cmds.spaceLocator(n='{}_fk_pole_aim'.format(name))[0]
    fk_pointC = cmds.spaceLocator(n='{}_fk_pole_pointC'.format(name))[0]
    cmds.parent(fk_pointC, fk_aim)
    cmds.matchTransform(fk_aim, fk_start_jnt)
    cmds.parent(fk_aim, fk_start_jnt)
    
    fk_mid_jnt = cmds.listRelatives(fk_start_jnt, c=True)[0] 
    cmds.aimConstraint(fk_end_jnt, fk_aim, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=fk_mid_jnt)
    cmds.pointConstraint(fk_mid_jnt, fk_pointC, skip=['z','y'])
    
    
    
    fk_pole = cmds.spaceLocator(n='{}_fk_pole'.format(name))[0]
    cmds.matchTransform(fk_pole, ik_pole)
    cmds.parent(fk_pole, fk_pointC)
    cmds.setAttr('{}.visibility'.format(fk_aim), False)
    