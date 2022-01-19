from J_maya_lib.J_maya_helper_lib import object_lib
from J_maya_lib.J_maya_UI_lib import components
import maya.cmds as cmds

import importlib

importlib.reload(object_lib)
importlib.reload(components)

class renamers:
    def __init__(self):
        self.name = 'general_renamer'
        if cmds.window(self.name, exists=True):
            cmds.deleteUI(self.name)
        cmds.window(self.name, title=self.name, w = 200, h = 400)
        cl = cmds.columnLayout()
        self.options = ['rename', 'duplicate and rename', 'create offset group','connect with pattern', 'duplicate nodes']
        self.rc = components.radio_collection(cl, self.options)
        self.sel = components.select_text_field(cl, 'selection', 100)
        self.pre = components.text_field(cl, 'pre', 100)
        self.before = components.text_field(cl, 'replace', 100)
        self.after = components.text_field(cl, 'with', 100)
        self.post = components.text_field(cl, 'post', 100)
        #need to replace these buttons
        cmds.button(label='execute', command=lambda x: self.renamer_functions())
        cmds.button(label='duplicate set', command=lambda x:object_lib.nonunique_obj_set())





        cmds.showWindow()
    def renamer_functions(self):
        objects = self.sel.get_value()
        pre = self.pre.get_value()[0]
        post=self.post.get_value()[0]
        custom = (self.before.get_value()[0], self.after.get_value()[0])
        if self.rc.get_value() == self.options[0]:
            object_lib.object_renamer(objects, pre=pre, custom=custom, post=post)
        elif self.rc.get_value() == self.options[1]:
            object_lib.dupl_renamer(objects, pre=pre, custom=custom, post=post)
        elif self.rc.get_value() == self.options[2]:
            object_lib.create_parent_grp(objects, pre=pre, custom=custom, post=post)
        elif self.rc.get_value() == self.options[3]:
            object_lib.connect_new_names(objects, pre=pre, custom=custom, post=post)
        elif self.rc.get_value() == self.options[4]:
            object_lib.dupl_node_connections(objects, pre=pre, custom=custom, post=post)
        