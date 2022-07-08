import maya.cmds as cmds
import pymel as pm
from J_maya_lib.J_maya_utility_lib import utility_helpers, utility_data


#flip names

#rename objects that were returned
def object_renamer(objects, pre = '', post = '', custom = ('', ''), check_contain_match_string=True):
    #check parameters
    try:
        objects = utility_helpers.turn_to_list(objects)
        utility_helpers.instance_exception('pre', pre, str)
        utility_helpers.instance_exception('post', post, str)
        utility_helpers.instance_exception('custom', custom, tuple)
    except Exception as inst:
        cmds.error(inst)
    if len(custom) != 2:
        cmds.error('custom must be a len of 2'.format(custom))
    #change custom to be all strings
    custom = (str(custom[0]), str(custom[1]))

    #add _ for pre and post
    for obj in reversed(objects):
        path_name, obj_name = utility_helpers.split_obj_name(obj)
        obj_new_name = utility_helpers.string_manip(obj_name, utility_data.JRename_Info(pre=pre, post=post, custom=custom), check_contain_match_string=check_contain_match_string)

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
    objects = utility_helpers.turn_to_list(objects)
    grps = []
    for obj in objects:
        grp_name = utility_helpers.string_manip(obj, pre = pre, post = post, custom = custom)
        grp = cmds.createNode('transform', n = grp_name)
        grps.append(grp)
        cmds.matchTransform(grp, obj)
        parents = cmds.listRelatives(obj, parent=True)
        if parents is not None:
            grp=cmds.parent(grp, parents[0])[0]
        cmds.setAttr('{}.{}'.format(grp, 'scaleX'), 1)
        cmds.setAttr('{}.{}'.format(grp, 'scaleY'), 1)
        cmds.setAttr('{}.{}'.format(grp, 'scaleZ'), 1)
        cmds.parent(obj, grp)
    return grps

def add_attributes(objects, attr, category = None):
    objects = utility_helpers.turn_to_list(objects)
    attr = utility_helpers.turn_to_list(attr)

    for obj in objects:
        #creating category
        if category != None:
            curr_attr = cmds.listAttr(obj)
            category_name = '_'
            while category_name in curr_attr:
                category_name = category_name + '_'
            cmds.addAttr(obj, ln = category_name, at='enum', en='{}:'.format(category))
            cmds.setAttr('{}.{}'.format(obj, category_name), e=True, cb=True)
        for a in attr:
            if a.type == 'bool':
                cmds.addAttr(obj, ln = a.name, at=a.type, k=True, dv=a.default)
                cmds.setAttr('{}.{}'.format(obj, a.name), e=True, keyable=True)
            elif a.type == 'float':
                cmds.addAttr(obj, ln = a.name, at=a.type, k=True, dv=a.default)
                cmds.setAttr('{}.{}'.format(obj, a.name), e=True, keyable=True)
                if a.max != None:
                    cmds.addAttr('{}.{}'.format(obj, a.name), e=True, max=a.max)
                if a.min != None:
                    cmds.addAttr('{}.{}'.format(obj, a.name), e=True, min=a.min)
            elif a.type == 'enum':
                cmds.addAttr(obj, ln = a.name, at=a.type, k=True, en=':'.join(a.default))
                cmds.setAttr('{}.{}'.format(obj, a.name), e=True, keyable=True)
            else:
                cmds.error('{} type not supported'.format(a.type))

def create_fk_cntrl(objects, pre='anim',  custom=('',''), post='', hierarchy=True, constraint = True, color=None):
    objects = utility_helpers.turn_to_list(objects)
    if hierarchy:
        objects = reverse_hierarchy(objects)
    circle_curve_grps = []
    
    for o in objects:
        #initial object
        print(o)
        circle_curve = cmds.circle(nr=(1, 0, 0), n=utility_helpers.string_manip(o, pre=pre, post=post, custom=custom))[0]
        cmds.delete(circle_curve, constructionHistory = True)
        cmds.matchTransform(circle_curve, o)
        off_grp = create_parent_grp(circle_curve)
        circle_curve_grps.append(off_grp[0])
        if constraint:
            cmds.parentConstraint(utility_helpers.split_obj_name(circle_curve)[1], o)
        else:
            cmds.pointConstraint(utility_helpers.split_obj_name(circle_curve)[1], o)
            cmds.connectAttr('{}.rotate'.format(circle_curve), '{}.rotate'.format(o))
        
        #get the hierarchy
        shapes = cmds.listRelatives(o, s=True)
        shapes = shapes if shapes != None else []
        children = [x for x in cmds.listRelatives(o, c=True) if x not in shapes]
        children = [x for x in children if cmds.nodeType(x) in ['joint', 'transform']]
        if hierarchy and children is not None:
            for s in children:
                child_grp = create_fk_cntrl(s)
                if len(child_grp) > 0:
                    cmds.parent(child_grp[0], circle_curve)
    if color != None:
        color_object(circle_curve_grps, color, hierarchy=hierarchy)
    return circle_curve_grps

#---------------------has pm equivalent
def reverse_hierarchy(objects):
    cmds.select(objects)
    cmds.select(hi=True)
    objects = cmds.ls(sl=True, long=True)
    objects_short = set(utility_helpers.convert_obj_names(objects))
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
        path_name, obj_name = utility_helpers.split_obj_name(obj)
        all_paths = cmds.ls(obj_name, allPaths=True)
        if len(all_paths) > 1:
            dupl_obj.append(obj)
    if(len(dupl_obj) == 0):
        cmds.warning('no duplicates were found')
        return
    return cmds.sets(dupl_obj, n = 'duplicates')

#list out all connections within a set of nodes
def get_connections(objects):
    objects = utility_helpers.turn_to_list(objects)
    short_objs = utility_helpers.convert_obj_names(objects)
    connections_with_conv = set()

    for obj in objects:
        # getting source and destination
        sources = cmds.listConnections(obj, s=True, d=False)
        if sources != None:
            sources = [x for x in sources if x in short_objs]
        else:
            sources=[]
        destinations = cmds.listConnections(obj, s=False, d=True)
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
def connect_new_names(objects, pre='', post='', custom=('', '')):
    connections = get_connections(objects)
    print(connections)
    for con in connections:
        driver = utility_helpers.string_manip(con[0], pre, post, custom)
        driven = utility_helpers.string_manip(con[1], pre, post, custom)
        cmds.connectAttr(driver, driven, f=True)

#---------------------has pm equivalent
def dupl_renamer(objects, pre = '', post = '', custom = ('', ''), check_contain_match_string=True):
    objects = reverse_hierarchy(utility_helpers.turn_to_list(objects))
    dupl_objects = []
    for obj in objects:
        cmds.select(obj)
        cmds.duplicate()[0]

        #parent duplicate
        dupl = cmds.ls(sl=True, long=True)[0]
        dupl_name = utility_helpers.string_manip(obj, pre=pre, post=post, custom=custom)
        cmds.rename(dupl, dupl_name)
        cmds.select(dupl_name)
        dupl_name = cmds.ls(sl=True, long=True)[0]
        dupl_objects.append(dupl_name)

        #duplicate selection
        cmds.select(hi=True)
        dupl_child = cmds.ls(sl=True, long=True)
        dupl_child.remove(dupl_name)

        #rename child objects
        object_renamer(dupl_child, pre, post, custom, check_contain_match_string)
    return dupl_objects

#---------------------has pm equivalent
def filter_node_types(objects, types, remove=True):
    objects = utility_helpers.turn_to_list(objects)
    types = utility_helpers.turn_to_list(types)
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
    objects = utility_helpers.turn_to_list(objects)
    print(objects)

    dupl_renamer(filter_node_types(objects, 'unitConversion'), pre, post, custom)
    connect_new_names(objects, pre, post, custom)
 
#---------------------has pm equivalent
def color_object(objects, color, hierarchy=False, index=True, reset=False):
    cmds.select(objects, hi=hierarchy)
    objects = cmds.ls(sl=True, long=True)
    objects = filter_node_types(objects, ['transform', 'joint'], remove=False)

    for obj in objects:
        shapes = cmds.listRelatives(obj, s=True)
        if cmds.nodeType(obj) == 'joint':
            set_color_attr(obj, color, index=index, reset=reset)
        if shapes != None:
            for s in shapes:
                set_color_attr(s, color, index=index, reset=reset)
#---------------------has pm equivalent
def set_color_attr(object, color, index=True, reset=False):
    cmds.setAttr('{}.overrideEnabled'.format(object), True)
    if index:
        cmds.setAttr('{}.overrideRGBColors'.format(object), 0)
        cmds.setAttr('{}.overrideColor'.format(object), color)
    if reset:
        cmds.setAttr('{}.overrideEnabled'.format(object), False)
        cmds.setAttr('{}.overrideRGBColors'.format(object), 0)
        cmds.setAttr('{}.overrideColor'.format(object), 0)

def filter_out_children_pm(objects):
    objects = utility_helpers.turn_to_list(objects)
    parent_objects = []
    # getting just the parent objects
    for obj in objects:
        if set(pm.core.listRelatives(obj, ap=True)).intersection(set(objects)) == set():
            parent_objects.append(obj)
    return parent_objects

def dupl_renamer_pm(objects, renameInfo:utility_data.JRename_Info):
    objects = utility_helpers.turn_to_list(objects)
    parent_objects = filter_out_children_pm(objects)
    dup_objects = pm.core.duplicate(parent_objects)
    for old_obj, new_obj in zip(parent_objects, dup_objects):
        new_obj.rename(utility_helpers.string_manip(old_obj, renameInfo))
    hierarchy = utility_helpers.obj_hierarchy(dup_objects, includeInitialObjects=False)
    for obj in hierarchy:
        obj.rename(utility_helpers.string_manip(obj.shortName(), renameInfo))

######----------------------------------still need to fix----------------------------------------------------
def dupl_node_connections_pm(objects, renameInfo:utility_data.JRename_Info):
    objects = utility_helpers.turn_to_list(objects)

    # dupl_renamer_pm(filter_node_types(objects, 'unitConversion'), renameInfo)
    # connect_new_names_pm(objects, renameInfo)

def filter_node_types_pm(objects, types, remove:bool = True):
    objects = utility_helpers.turn_to_list(objects)
    types = utility_helpers.turn_to_list(types)
    if remove:
        return [x for x in objects if pm.core.general.nodeType(x) not in types]
    return [x for x in objects if pm.core.general.nodeType(x) in types]  

def color_object_pm(objects, color, hierarchy:bool = False, index:bool = True, reset:bool = False):
    if hierarchy: 
        objects = utility_helpers.obj_hierarchy(objects)
        objects = filter_node_types_pm(objects, ['transform', 'joint'], remove=False)

    #take out transform if we can
    for obj in objects:
        shapes = pm.core.general.listRelatives(obj, s=True)
        if pm.core.general.nodeType(obj) == 'joint':
            set_color_attr_pm(obj, color, index=index, reset=reset)
        if shapes != None:
            for s in shapes:
                set_color_attr_pm(s, color, index=index, reset=reset)

def set_color_attr_pm(object, color, index:bool = True, reset:bool = False):
        object.overrideEnabled.set(True)
        if index:
            object.overrideRGBColors.set(0)
            object.overrideColor.set(color)
        if reset:
            object.overrideEnabled.set(False)
            object.overrideRGBColors.set(0)
            object.overrideColor.set(0)
