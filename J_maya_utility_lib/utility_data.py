import maya.cmds as cmds
import math
from typing import TypeVar

SelfJVector = TypeVar("SelfJVector", bound="JVector")

class JVector:
    def __init__(self, values:'list[float]'):
        self.values = values
        self.length = len(values)
    def __add__(self, obj:SelfJVector):
        if self.length != obj.length:
            cmds.warning('length mismatch')
        result = []
        for s, o in zip(self.values, obj.values):
            result.append(s+o)
        return JVector(result)
    def __sub__(self, obj:SelfJVector):
        if self.length != obj.length:
            cmds.warning('length mismatch')
        result = []
        for s, o in zip(self.values, obj.values):
            result.append(s-o)
        return JVector(result)
    def __mult__(self, obj:SelfJVector):
        if self.length != obj.length:
            cmds.warning('length mismatch')
        result = []
        for s, o in zip(self.values, obj.values):
            result.append(s*o)
        return JVector(result)
    def dot(self, obj):
        result = self.__mult__(obj)
        sum = 0
        for r in result.values:
            sum = sum+r
        return sum
    def mag(self):
        result = math.sqrt(self.dot(self))
        return result


class JObject_Attr_Info:
    def __init__(self, name:str, type:str, default, min=None, max=None):
        self.name = name
        self.type = type
        self.default = default
        self.min = min
        self.max = max

class JRename_Info:
    def __init__(self, pre:str = '', post:str = '', custom:tuple = ('', '')):
        self.pre = pre
        self.post = post
        self.custom = custom