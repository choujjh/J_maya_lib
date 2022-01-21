from ntpath import join
from tracemalloc import start
import maya.cmds as cmds
import importlib
from J_maya_lib.J_maya_helper_lib import helpers
from J_maya_lib.J_maya_helper_lib import object_lib

importlib.reload(helpers)
importlib.reload(object_lib)


def create_ind_ik_handles(joints, pre = '', post = 'Handle', custom = ('', ''), rot_plane_slv=True):
    # get the hierarchy
    joints = helpers.turn_to_list(joints)
    cmds.select(joints)
    cmds.select(hi=True)
    joints = object_lib.filter_node_types(cmds.ls(sl=True, long=True), 'joint', remove=False)
    joint_dict = {}

    # get every joint and its parent
    for j in joints:
        parent, child = helpers.split_obj_name(j)[0], j
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
        handle = helpers.split_obj_name(j)
        handle = helpers.string_manip(handle[1], pre = pre, post = post, custom = custom)
        if rot_plane_slv:
            ik_handles.append(cmds.ikHandle( n = handle, sj = j, ee = joint_dict[j][0], sol = 'ikRPsolver')[0])
        else:
            ik_handles.append(cmds.ikHandle(n = handle, sj = j, ee = joint_dict[j][0], sol = 'ikSCsolver')[0])
    return ik_handles

class joint_info:
    def __init__(self, color=5, radius=0.5):
        self.color = color
        self.radius = radius
def set_radius(joints, radius):
    joints = helpers.turn_to_list(joints)
    for j in joints:
        if cmds.nodeType(j) == 'joint':
            cmds.setAttr('{}.radius'.format(j), radius)

def setup_ik_chain(ik_start_jnt, ik_mid_jnt, ik_end_jnt, start_jnt):
    #ik joint chain
    handle, effector = cmds.ikHandle( n = helpers.string_manip(ik_start_jnt, post = 'handle'), sj = ik_start_jnt, ee = ik_end_jnt, sol = 'ikRPsolver')
    effector = cmds.rename(effector, helpers.string_manip(ik_start_jnt, post = 'eff'))
    #create offset grps
    loc_start = cmds.spaceLocator(n = helpers.string_manip(ik_start_jnt, pre = 'anim', post = 'locOffset'))[0]
    loc_handle = cmds.spaceLocator(n = helpers.string_manip(ik_end_jnt, pre = 'anim', post = 'handle_locOffset'))[0]
    loc_pole_vec = cmds.spaceLocator(n = helpers.string_manip(ik_end_jnt, pre = 'anim', post = 'pullVec_locOffset'))[0]
    #matching transforms
    cmds.matchTransform(loc_start, ik_start_jnt)
    cmds.matchTransform(loc_handle, ik_end_jnt)
    #attach everything
    cmds.pointConstraint(loc_start, ik_start_jnt)
    cmds.pointConstraint(loc_handle, handle)
    ik_grp = cmds.createNode('transform', n=helpers.string_manip(start_jnt, post = 'ik_grp01'))
    cmds.parent([loc_start, loc_handle, ik_grp])
    #set where the pull vector will be
    #get the pull value
    setup_pull_vec(ik_start_jnt, ik_mid_jnt, ik_end_jnt, handle, loc_pole_vec, ik_grp)
    
def setup_pull_vec(ik_start_jnt, ik_mid_jnt, ik_end_jnt, handle, loc_pole_vec, ik_grp):
    current_pole_vec = helpers.vector([cmds.getAttr('{}.poleVectorX'.format(handle)), cmds.getAttr('{}.poleVectorY'.format(handle)), cmds.getAttr('{}.poleVectorZ'.format(handle))])
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
    cmds.setAttr('{}.translateY'.format(loc_pole_vec), cmds.getAttr('{}.translateY'.format(loc_pole_vec)) * 2)
    cmds.delete(loc_pointC)
    cmds.parent(loc_pole_vec, w=True)
    cmds.delete(temp_grp)
    #create an offset grp
    pole_grp=object_lib.create_parent_grp(loc_pole_vec)[0]
    cmds.parent(pole_grp, ik_grp)
    cmds.poleVectorConstraint(loc_pole_vec, handle)

def setup_jnt_chain(start_jnt, end_jnt, switch_cntrl, ik_info, fk_info, jnt_info):
    helpers.select_obj_hierarchy(start_jnt)
    set_radius(cmds.ls(sl=True, long=True), jnt_info.radius)
    #ik joints
    ik_start_jnt = object_lib.dupl_renamer(start_jnt, post = 'ik')[0]
    helpers.select_obj_hierarchy(ik_start_jnt)
    set_radius(cmds.ls(sl=True, long=True), ik_info.radius)
    ik_mid_jnt = cmds.listRelatives(ik_start_jnt, c=True)[0]
    ik_end_jnt = helpers.string_manip(helpers.split_obj_name(end_jnt)[1], post = 'ik')

    #fk joints
    fk_start_jnt = object_lib.dupl_renamer(start_jnt, post = 'fk')[0]
    helpers.select_obj_hierarchy(fk_start_jnt)
    set_radius(cmds.ls(sl=True, long=True), fk_info.radius)

    setup_ik_chain(ik_start_jnt, ik_mid_jnt, ik_end_jnt, start_jnt)

    object_lib.create_fk_cntrl(fk_start_jnt)





