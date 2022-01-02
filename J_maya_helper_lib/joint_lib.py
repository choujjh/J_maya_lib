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

def create_spline_ik_handles(joints, name='', type='individual', rot_plane_slv=True):
    if type == 'individual':
        print('TODO')
    elif type == 'complete_heirarchy':
        print('TODO')
    elif type == 'chain':
        print('TODO')