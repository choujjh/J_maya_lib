import maya.cmds as cmds
import math

def instance_exception(var_name, var, type):
    if not isinstance(var, type):
        raise Exception('{} {} needs to be a {}'.format(var_name, var, str(type)))

# def comtains_nonunique_exception(objects):


#string manipulation stuff
def split_obj_name(obj):
    path_name = obj[:obj.rfind('|')]
    obj_name = obj[obj.rfind('|') + 1:]
    return path_name, obj_name

def string_manip(obj_name, pre = '', post = '', custom = ('', ''), check_contain_match_string=True):
    if custom[0].find(custom[1]) != -1:
        check_contain_match_string = False
    obj_name = split_obj_name(obj_name)[1]
    if len(pre) > 0 and not pre.endswith('_'):
        pre = '{}_'.format(pre)
    if len(post) > 0 and not post.startswith('_'):
        post = '_{}'.format(post)
    if check_contain_match_string:
        if obj_name.find(custom[1]) == -1:
            obj_name = obj_name.replace(custom[0], custom[1])
    else:
        obj_name = obj_name.replace(custom[0], custom[1])
    obj_new_name = pre + obj_name + post
    return obj_new_name

class vector:
    def __init__(self, values):
        self.values = values
        self.length = len(values)
    def __add__(self, obj):
        if self.length != obj.length:
            cmds.warning('length mismatch')
        result = []
        for s, o in zip(self.values, obj.values):
            result.append(s+o)
        return vector(result)
    def __sub__(self, obj):
        if self.length != obj.length:
            cmds.warning('length mismatch')
        result = []
        for s, o in zip(self.values, obj.values):
            result.append(s-o)
        return vector(result)
    def __mult__(self, obj):
        if self.length != obj.length:
            cmds.warning('length mismatch')
        result = []
        for s, o in zip(self.values, obj.values):
            result.append(s*o)
        return vector(result)
    def dot(self, obj):
        result = self.__mult__(obj)
        sum = 0
        for r in result.values:
            sum = sum+r
        return sum
    def mag(self):
        result = math.sqrt(self.dot(self))
        return result
    

def turn_to_list(current_list):
    if not isinstance(current_list, list):
        return [current_list]
    return current_list

def convert_obj_names(objects, long=False):
    objects = turn_to_list(objects)
    if not long:
        return [split_obj_name(x)[1] for x in objects]
    cmds.select(objects)
    return cmds.ls(sl=True, long=True)

def select_obj_hierarchy(object):
    cmds.select(object)
    cmds.select(hi=True)

