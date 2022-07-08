import pymel as pm
from J_maya_lib.J_maya_utility_lib import utility_data

def instance_exception(var_name, var, type):
    if not isinstance(var, type):
        raise Exception('{} {} needs to be a {}'.format(var_name, var, str(type)))

#string manipulation stuff
def split_obj_name(obj):
    path_name = obj[:obj.rfind('|')]
    obj_name = obj[obj.rfind('|') + 1:]
    return path_name, obj_name

def string_manip(object, renameInfo:utility_data.JRename_Info , check_contain_match_string=True):
    if renameInfo.custom[0].find(renameInfo.custom[1]) != -1:
        check_contain_match_string = False
    obj_name = object
    if not isinstance(obj_name, str):
        obj_name = object.nodeName()
    if len(renameInfo.pre) > 0 and not renameInfo.pre.endswith('_'):
        renameInfo.pre = '{}_'.format(renameInfo.pre)
    if len(renameInfo.post) > 0 and not renameInfo.post.startswith('_'):
        renameInfo.post = '_{}'.format(renameInfo.post)
    if check_contain_match_string:
        obj_name = obj_name.replace(renameInfo.custom[0], renameInfo.custom[1])
    return renameInfo.pre + obj_name + renameInfo.post

def turn_to_list(current_list):
    if not isinstance(current_list, list):
        return [current_list]
    return current_list

def obj_hierarchy(objects, includeInitialObjects:bool=True):
    hierarchy = pm.core.general.listRelatives(objects, ad=True)
    object_copy = objects.copy()
    if includeInitialObjects==True:
        object_copy=[]
    if hierarchy == None:
        return object_copy
    object_copy.extend(hierarchy[::-1])
    return object_copy

