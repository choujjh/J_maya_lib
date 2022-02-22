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

        self.__info_frame__()
        self.__utility_frame__()
        self.__fk_frame__()

        self.win.J_show_window()

    def __info_frame__(self):
        self.info_frame_info = frameworks.J_frameLayout(self.main_layout, 220, 165, 'info', collapsable=False)
        self.info_frame_info_col = frameworks.J_columnLayout(self.info_frame_info, 220, 0)
        self.info_cb = components.check_box(self.info_frame_info_col, 'selection')
        self.info_sel = components.select_text_field(self.info_frame_info_col, 'object(s)', 100)
        self.info_cb.on_update(on_function=lambda x: self.info_sel.editable(False), off_function=lambda y: self.info_sel.editable(True))
        self.info_pre = components.text_field(self.info_frame_info_col, 'pre', 100)
        self.info_replace = components.text_field(self.info_frame_info_col, 'replace', 100)
        self.info_with = components.text_field(self.info_frame_info_col, 'with', 100)
        self.info_post = components.text_field(self.info_frame_info_col, 'post', 100)

    def __get_info__(self):
        objects = []
        if not self.info_cb.get_value():
            objects = self.info_sel.get_value()
        else:
            objects = cmds.ls(sl=True, long=True)
        pre = self.info_pre.get_value()[0]
        post=self.info_post.get_value()[0]
        custom = (self.info_replace.get_value()[0], self.info_with.get_value()[0])
        return {
            'objects': objects,
            'pre': pre,
            'post': post,
            'custom': custom
        }

    def __utility_frame__(self):
        self.util_frame = frameworks.J_frameLayout(self.main_layout, 220, 175, 'Utility')
        self.util_frame_col = frameworks.J_columnLayout(self.util_frame, 220, 0)
        self.options = ['rename', 'duplicate and rename', 'create offset group','connect with pattern', 'duplicate nodes']
        self.util_rc = components.radio_collection(self.util_frame_col, self.options)
        
        components.button(self.util_frame_col, 'execute', lambda x: self.__utility_functions__())
        components.separator(self.util_frame_col)
        components.button(self.util_frame_col, 'duplicate set', lambda x: object_lib.nonunique_obj_set())

    def __fk_frame__(self):
        self.fk_frame = frameworks.J_frameLayout(self.main_layout, 220, 75, 'FK')
        self.fk_frame_col = frameworks.J_columnLayout(self.fk_frame, 220, 0)
        self.fk_cb = components.check_box(self.fk_frame_col, 'hierarchy')
        components.button(self.fk_frame_col, 'create fk chain', lambda x: self.__fk_functions__())
    def __fk_functions__(self):
        info = self.__get_info__()
        object_lib.create_fk_cntrl(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'], hierarchy=self.fk_cb.get_value())

    def __utility_functions__(self):
        info = self.__get_info__()
        if self.util_rc.get_value() == self.options[0]:
            object_lib.object_renamer(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'])
        elif self.util_rc.get_value() == self.options[1]:
            object_lib.dupl_renamer(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'])
        elif self.util_rc.get_value() == self.options[2]:
            object_lib.create_parent_grp(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'])
        elif self.util_rc.get_value() == self.options[3]:
            object_lib.connect_new_names(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'])
        elif self.util_rc.get_value() == self.options[4]:
            object_lib.dupl_node_connections(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'])
        