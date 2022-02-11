import maya.cmds as cmds
from J_maya_lib.J_maya_UI_lib import UI_helpers

#frameLayout
#columnLayout
#rowLayout
#rowColumnLayout

#use decorator pattern?

#width height
#parent
#hide layout

import importlib

importlib.reload(UI_helpers)

class J_layout:
    def __init__(self, parent, width, height):
        self.parent = parent
        self.width = width
        self.height = height
        self.name = None

    def get_width_height(self):
        return self.width, self.height
    def get_parent(self):
        return self.parent
    def get_all_parents(self):
        objs = []
        currObj = self.get_parent()
        while currObj != None:
            objs.append(currObj)
            if isinstance(currObj, J_layout):
                currObj = currObj.get_parent()
            else:
                break
        return objs

    def redim_layout(self, expand, width=0, height=0):
        cmds.error("collapse_layout musht be implemented in children")

    def redim_hierarchy_layout(self, expand, width=False, height=True):
        width= self.width if width else 0
        height= self.height if height else 0
        parents = self.get_all_parents()
        self.redim_layout(expand, width, height)
        for p in parents:
            p.redim_layout(expand, width, height)
    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name


class J_window(J_layout):
    def __init__(self, width, height, title, restart=True):
        super().__init__(None, width, height)
        if restart and cmds.window(title, exists=True):
            cmds.deleteUI(title)
        super().set_name((cmds.window(title, title=title, w=width, h=height)))

    def redim_layout(self, expand=True, width=0, height=0):
        curr_height = cmds.window(super().get_name(), q=True, height=True)
        curr_width = cmds.window(super().get_name(), q=True, width=True)
        if not expand:
            width = -width
            height = -height
        if abs(width) >= 1:
            cmds.window(super().get_name(), e=True, w=curr_width+width)
        if abs(height) >= 1:
            cmds.window(super().get_name(), e=True, h=curr_height+height)
        
        
    def J_show_window(self):
        cmds.showWindow(super().get_name())
class J_frameLayout(J_layout):
    def __init__(self, parent, width, height, collapsable=True):
        super().__init__(parent, width, height-25)
        super().set_name((cmds.frameLayout(cll=collapsable, w=width, h=height, p=UI_helpers.get_UI_parent_string(parent))))
        self.collapsable = collapsable
        if collapsable:
            cmds.frameLayout(super().get_name(), e=True, cc = lambda: super(J_frameLayout, self).redim_hierarchy_layout(False))
            cmds.frameLayout(super().get_name(), e=True, ec = lambda: super(J_frameLayout, self).redim_hierarchy_layout(True))
    def redim_layout(self, expand=True, width=0, height=0):
        curr_height = cmds.frameLayout(super().get_name(), q=True, h=True)
        if self.collapsable:
            if expand:
                cmds.frameLayout(super().get_name(), e=True, h=curr_height)
            else:
                cmds.frameLayout(super().get_name(), e=True, h=25)
        
    
        
        
