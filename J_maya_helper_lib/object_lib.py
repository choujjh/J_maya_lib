import maya.cmds as cmds
import importlib
from J_maya_lib.J_maya_helper_lib import helpers

importlib.reload(helpers)

#rename objects that were returned
def object_renamer(objects, pre = '', post = '', custom = ('', ''), check_contain_match_string=True):
    #check parameters
    try:
        objects = helpers.turn_to_list(objects)
        helpers.instance_exception('pre', pre, str)
        helpers.instance_exception('post', post, str)
        helpers.instance_exception('custom', custom, tuple)
    except Exception as inst:
        cmds.error(inst)
    if len(custom) != 2:
        cmds.error('custom must be a len of 2'.format(custom))
    #change custom to be all strings
    custom = (str(custom[0]), str(custom[1]))

    #add _ for pre and post
    for obj in reversed(objects):
        path_name, obj_name = helpers.split_obj_name(obj)
        obj_new_name = helpers.string_manip(obj_name, pre=pre, post=post, custom=custom, check_contain_match_string=check_contain_match_string)

        if cmds.objExists(obj):
            # checks to see if the replacement name hasn't been taken yet
            if len(cmds.ls(obj_new_name, allPaths=True)) == 0:
                cmds.rename(obj, obj_new_name)
                continue
            elif obj_new_name == obj_name:
                continue
        cmds.rename(obj, obj)

#creates a padding parent group
def create_parent_grp(objects, pre='', post='_offset_grp01', custom=('','')):
    objects = helpers.turn_to_list(objects)
    for obj in objects:
        grp_name = helpers.string_manip(obj, pre = pre, post = post, custom = custom)
        grp = cmds.createNode('transform', n = grp_name)
        cmds.matchTransform(grp, obj)
        parents = cmds.listRelatives(obj, parent=True)
        if parents is not None:
            cmds.parent(grp, parents[0])
        cmds.setAttr('{}.{}'.format(grp, 'scaleX'), 1)
        cmds.setAttr('{}.{}'.format(grp, 'scaleY'), 1)
        cmds.setAttr('{}.{}'.format(grp, 'scaleZ'), 1)
        cmds.parent(obj, grp)

#gets the highest parent of selected nodes (all selected children won't be returned)
def reverse_hierarchy(objects):
    cmds.select(objects)
    cmds.select(hi=True)
    objects = cmds.ls(sl=True, long=True)
    objects_short = set(helpers.convert_obj_names(objects))
    high_hierarchy = []
    for obj in objects:
        rel = cmds.listRelatives(obj, p=True)
        if rel == None:
            high_hierarchy.append(obj)
        elif rel[0] not in objects_short:
            high_hierarchy.append(obj)
    cmds.select(high_hierarchy)
    return high_hierarchy

#creates a set of all nonunique objects
def nonunique_obj_set():
    objects = cmds.ls(long=True)
    dupl_obj = []
    for obj in objects:
        path_name, obj_name = helpers.split_obj_name(obj)
        all_paths = cmds.ls(obj_name, allPaths=True)
        if len(all_paths) > 1:
            dupl_obj.append(obj)
    if(len(dupl_obj) == 0):
        cmds.warning('no duplicates were found')
        return
    return cmds.sets(dupl_obj, n = 'duplicates')

#list out all connections within a set of nodes
def get_connections(objects):
    objects = helpers.turn_to_list(objects)
    short_objs = helpers.convert_obj_names(objects)
    connections_with_conv = set()

    for obj in objects:
        # getting source and destination
        sources = cmds.listConnections(obj, s=True, d=False)
        if sources != None:
            sources = [x for x in sources if x in short_objs]
        else:
            sources=[]
        destinations = [x for x in cmds.listConnections(obj, s=False, d=True) if x in short_objs]
        if destinations != None:
            destinations = [x for x in destinations if x in short_objs]
        else:
            destinations = []


        # separating out connections to have the right ordering
        conn_driver = cmds.listConnections(obj, c=True, p=True)[::2]
        conn_driven = cmds.listConnections(obj, c=True, p=True)[1::2]
        for driver, driven in zip(conn_driver, conn_driven):
            if driven.split('.')[0] in sources:
                connections_with_conv.add((driven, driver))
            elif driven.split('.')[0] in destinations:
                connections_with_conv.add((driver, driven))

    # combine unit conversions
    connections_with_conv = list(connections_with_conv)
    connections = []
    for driver in connections_with_conv:
        if cmds.nodeType(driver[1]) == 'unitConversion':
            for driven in connections_with_conv:
                if driven[0].split('.')[0] == driver[1].split('.')[0]:
                    connections.append((driver[0], driven[1]))
                    continue
        elif cmds.nodeType(driver[0]) != 'unitConversion' and cmds.nodeType(driver[1]) != 'unitConversion':
            connections.append(driver)
    return connections

#connect with a new naming alias
def connect_new_names(connections, pre='', post='', custom=('', '')):
    for con in connections:
        driver = helpers.string_manip(con[0], pre, post, custom)
        driven = helpers.string_manip(con[1], pre, post, custom)
        cmds.connectAttr(driver, driven, f=True)

#duplicate and rename
def dupl_renamer(objects, pre = '', post = '', custom = ('', ''), check_contain_match_string=True):
    objects = reverse_hierarchy(helpers.turn_to_list(objects))
    for obj in objects:
        cmds.select(obj)
        cmds.duplicate()[0]

        #parent duplicate
        dupl = cmds.ls(sl=True, long=True)[0]
        dupl_name = helpers.string_manip(obj, pre=pre, post=post, custom=custom)
        cmds.rename(dupl, dupl_name)
        cmds.select(dupl_name)
        dupl_name = cmds.ls(sl=True, long=True)[0]

        #duplicate selection
        cmds.select(hi=True)
        dupl_child = cmds.ls(sl=True, long=True)
        dupl_child.remove(dupl_name)

        #rename child objects
        object_renamer(dupl_child, pre, post, custom, check_contain_match_string)

#removes all node types and returns it
def filter_node_types(objects, types, remove=True):
    objects = helpers.turn_to_list(objects)
    types = helpers.turn_to_list(types)
    ret_obj = []
    for obj in objects:
        if remove:
            if cmds.nodeType(obj) not in types:
                ret_obj.append(obj)
        else:
            if cmds.nodeType(obj) in types:
                ret_obj.append(obj)
    return ret_obj

#duplicates nodes and retains connections
def dupl_node_connections(objects, pre='', post='', custom=('', '')):
    objects = helpers.turn_to_list(objects)
    connections = get_connections(objects)

    dupl_renamer(filter_node_types(objects, 'unitConversion'), pre, post, custom)
    connect_new_names(connections, pre, post, custom)