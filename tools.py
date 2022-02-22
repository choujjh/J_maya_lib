from J_maya_lib.J_maya_helper_lib import object_lib
from J_maya_lib.J_maya_UI_lib import components, frameworks
import maya.cmds as cmds

import importlib

importlib.reload(object_lib)
importlib.reload(components)
importlib.reload(frameworks)

class master_tool:
    def __init__(self):

        self.name = 'master_tool'
        self.win = frameworks.J_window(None, 220, 350, self.name)
        self.scroll = frameworks.J_scrollLayout(self.win, 220, 350)
        self.main_layout = frameworks.J_columnLayout(self.scroll, 220, 350)
        self.info_frame()

        self.utility_frame()


        self.win.J_show_window()

    def info_frame(self):
        self.info_frame_info = frameworks.J_frameLayout(self.main_layout, 220, 165, "info", collapsable=False)
        self.info_frame_info_col = frameworks.J_columnLayout(self.info_frame_info, 220, 0)
        self.info_cb = components.check_box(self.info_frame_info_col, 'selection')
        self.info_sel = components.select_text_field(self.info_frame_info_col, 'object(s)', 100)
        self.info_cb.on_update(on_function=lambda x: self.info_sel.editable(False), off_function=lambda y: self.info_sel.editable(True))
        self.info_pre = components.text_field(self.info_frame_info_col, 'pre', 100)
        self.info_replace = components.text_field(self.info_frame_info_col, 'replace', 100)
        self.info_with = components.text_field(self.info_frame_info_col, 'with', 100)
        self.info_post = components.text_field(self.info_frame_info_col, 'post', 100)

    def utility_frame(self):
        self.util_frame = frameworks.J_frameLayout(self.main_layout, 220, 175, "Utility")
        self.util_frame_col = frameworks.J_columnLayout(self.util_frame, 220, 0)
        self.options = ['rename', 'duplicate and rename', 'create offset group','connect with pattern', 'duplicate nodes']
        self.util_rc = components.radio_collection(self.util_frame_col, self.options)
        
        components.button(self.util_frame_col, 'execute', lambda x: self.utility_functions())
        components.separator(self.util_frame_col)
        components.button(self.util_frame_col, 'duplicate set', lambda x: object_lib.nonunique_obj_set())
    def utility_functions(self):
        objects = []
        if not self.util_cb.get_value():
            objects = self.info_sel.get_value()
        else:
            objects = cmds.ls(sl=True, long=True)
        pre = self.info_pre.get_value()[0]
        post=self.info_post.get_value()[0]
        custom = (self.info_replace.get_value()[0], self.info_with.get_value()[0])
        if self.util_rc.get_value() == self.options[0]:
            object_lib.object_renamer(objects, pre=pre, custom=custom, post=post)
        elif self.util_rc.get_value() == self.options[1]:
            object_lib.dupl_renamer(objects, pre=pre, custom=custom, post=post)
        elif self.util_rc.get_value() == self.options[2]:
            object_lib.create_parent_grp(objects, pre=pre, custom=custom, post=post)
        elif self.util_rc.get_value() == self.options[3]:
            object_lib.connect_new_names(objects, pre=pre, custom=custom, post=post)
        elif self.util_rc.get_value() == self.options[4]:
            object_lib.dupl_node_connections(objects, pre=pre, custom=custom, post=post)
        