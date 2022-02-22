import maya.cmds as cmds
import importlib
from J_maya_lib.J_maya_helper_lib import helpers


class attr_info:
    def __init__(self, name, type, default, min=None, max=None):
        self.name = name
        self.type = type
        self.default = default
        self.min = min
        self.max = max

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
    grps = []
    for obj in objects:
        grp_name = helpers.string_manip(obj, pre = pre, post = post, custom = custom)
        grp = cmds.createNode('transform', n = grp_name)
        grps.append(grp)
        cmds.matchTransform(grp, obj)
        parents = cmds.listRelatives(obj, parent=True)
        if parents is not None:
            cmds.parent(grp, parents[0])
        cmds.setAttr('{}.{}'.format(grp, 'scaleX'), 1)
        cmds.setAttr('{}.{}'.format(grp, 'scaleY'), 1)
        cmds.setAttr('{}.{}'.format(grp, 'scaleZ'), 1)
        cmds.parent(obj, grp)
    return grps

def add_attributes(objects, attr, category = None):
    objects = helpers.turn_to_list(objects)
    attr = helpers.turn_to_list(attr)

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

def create_fk_cntrl(objects, pre='anim',  custom=('',''), post='', hierarchy=True, constraint = True):
    objects = helpers.turn_to_list(objects)
    if hierarchy:
        objects = reverse_hierarchy(objects)
    circle_curve_grps = []
    for o in objects:
        #initial object
        circle_curve = cmds.circle(nr=(1, 0, 0), n=helpers.string_manip(o, pre=pre, post=post, custom=custom))[0]
        cmds.delete(circle_curve, constructionHistory = True)
        cmds.matchTransform(circle_curve, o)
        off_grp = create_parent_grp(circle_curve)
        circle_curve_grps.append(off_grp[0])
        if constraint:
            cmds.parentConstraint(circle_curve, o)
        else:
            cmds.pointConstraint(circle_curve, o)
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
    return circle_curve_grps

def anim_circle(scale, rotateAngle=[0, 0, 0], center=[0, 0, 0], n='nurbsCircle', degree=3, sections=8):
    cntrl = cmds.circle(r=scale, d=degree, s=sections, ch=False, n=n, c=center)[0]
    cmds.xform(cntrl, ro=rotateAngle)
    # cmds.setAttr(cntrl+'.rotate', rotateAngle)
    cmds.makeIdentity(cntrl, apply=True, t=True, r=True, s=True, n=False, pn=True)
    return cntrl

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
        destinations = cmds.listConnections(obj, s=False, d=True)
        if destinations != None:
            destinations = [x for x in destinations if x in short_objs]
        else:
            destinations = []
        print('obj: {}'.format(obj))
        print('source: {}'.format(sources))
        print('destination: {}'.format(destinations))

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
        driver = helpers.string_manip(con[0], pre, post, custom)
        driven = helpers.string_manip(con[1], pre, post, custom)
        cmds.connectAttr(driver, driven, f=True)

#duplicate and rename
def dupl_renamer(objects, pre = '', post = '', custom = ('', ''), check_contain_match_string=True):
    objects = reverse_hierarchy(helpers.turn_to_list(objects))
    dupl_objects = []
    for obj in objects:
        cmds.select(obj)
        cmds.duplicate()[0]

        #parent duplicate
        dupl = cmds.ls(sl=True, long=True)[0]
        dupl_name = helpers.string_manip(obj, pre=pre, post=post, custom=custom)
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
    print(objects)

    dupl_renamer(filter_node_types(objects, 'unitConversion'), pre, post, custom)
    connect_new_names(objects, pre, post, custom)