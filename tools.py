from J_maya_lib.J_maya_utility_lib import object_lib, joint_lib
from J_maya_lib.J_maya_UI_lib import components, frameworks
import maya.cmds as cmds

import importlib

importlib.reload(object_lib)
importlib.reload(components)
importlib.reload(frameworks)
importlib.reload(joint_lib)

class master_tool:
    def __init__(self):
        self.width = 245

        self.name = 'master_tool'
        self.win = frameworks.J_window(None, self.width, 470, self.name)
        self.scroll = frameworks.J_scrollLayout(self.win, self.width, 350)
        self.main_layout = frameworks.J_columnLayout(self.scroll, self.width, 350)

        self.__info_frame__()
        self.__utility_frame__()
        self.__fk_frame__()
        self.__set_color_frame__()
        self.__joint_setup_frame()
        # components.separator(self.main_layout)

        self.win.J_show_window()
    def __info_frame__(self):
        self.info_frame_info = frameworks.J_frameLayout(self.main_layout, self.width, 165, 'Info', collapsable=False)
        self.info_frame_info_col = frameworks.J_columnLayout(self.info_frame_info, self.width, 0)

        #check box
        self.info_cb = components.check_box(self.info_frame_info_col, 'selection', value=True)
        #object selection box
        self.info_sel = components.select_text_field(self.info_frame_info_col, 'object(s)', 100, 135)
        self.info_sel.editable(False)
        self.info_cb.on_update(on_function=lambda x: self.info_sel.editable(False), off_function=lambda y: self.info_sel.editable(True))

        self.info_pre = components.text_field(self.info_frame_info_col, 'pre', 100, 135)
        self.info_replace = components.text_field(self.info_frame_info_col, 'replace', 100, 135)
        self.info_with = components.text_field(self.info_frame_info_col, 'with', 100, 135)
        self.info_post = components.text_field(self.info_frame_info_col, 'post', 100, 135)
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
        self.util_frame = frameworks.J_frameLayout(self.main_layout, self.width, 175, 'Utility')
        self.util_frame_col = frameworks.J_columnLayout(self.util_frame, self.width, 0)
        self.options = ['rename', 'duplicate and rename', 'create offset group','connect with pattern', 'duplicate nodes']
        self.util_rc = components.radio_collection(self.util_frame_col, self.options)
        
        components.button(self.util_frame_col, 'apply', lambda x: self.__utility_functions__())
        components.button(self.util_frame_col, 'duplicate set', lambda x: object_lib.nonunique_obj_set())
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

    def __fk_frame__(self):
        self.fk_frame = frameworks.J_frameLayout(self.main_layout, self.width, 75, 'FK')
        self.fk_frame_col = frameworks.J_columnLayout(self.fk_frame, self.width, 0)
        self.fk_cb = components.check_box(self.fk_frame_col, 'hierarchy')
        components.button(self.fk_frame_col, 'create fk chain', lambda x: self.__fk_functions__())
    def __fk_functions__(self):
        info = self.__get_info__()
        object_lib.create_fk_cntrl(info['objects'], pre=info['pre'], custom=info['custom'], post=info['post'], hierarchy=self.fk_cb.get_value())

    def __set_color_frame__(self):
        self.sc_frame = frameworks.J_frameLayout(self.main_layout, self.width, 200, 'Set Color')
        self.sc_frame_col = frameworks.J_columnLayout(self.sc_frame, self.width, 0)

        self.sc_color_picker = components.color_picker(self.sc_frame_col, horz_cells=12, width=self.width, height=65)
        self.sc_cb_hi = components.check_box(self.sc_frame_col, 'hierarchy')
        self.sc_cb_sel = components.check_box(self.sc_frame_col, 'selection', value=True)
        self.sc_sel = components.select_text_field(self.sc_frame_col, 'object(s)', 100, 135)
        self.sc_sel.editable(False)
        self.sc_cb_sel.on_update(on_function=lambda x: self.sc_sel.editable(False), off_function=lambda y: self.sc_sel.editable(True))

        components.button(self.sc_frame_col, 'add color', lambda x: self.__set_color_function__())
        components.button(self.sc_frame_col, 'reset', lambda x: self.__set_color_function__(reset=True))
    def __set_color_function__(self, reset=False):
        objects = self.sc_sel.get_value()
        if self.sc_sel:
            objects = cmds.ls(sl=True, long=True)
        hierarchy = self.sc_cb_hi.get_value()
        object_lib.color_object(objects, self.sc_color_picker.get_value(), hierarchy=hierarchy, reset=reset)

    def __joint_setup_frame(self):
        self.js_frame = frameworks.J_frameLayout(self.main_layout, self.width, 445, 'Joint Setup')
        self.js_frame_col = frameworks.J_columnLayout(self.js_frame, self.width, 0)

        #color UI components
        self.js_color_picker = components.color_picker(self.js_frame_col, horz_cells=12, width=self.width, height=65)
        components.separator(self.js_frame_col)
        self.js_ik_jnt_color = components.button_color_index_slider(self.js_frame_col, "ik joint", 100, 130, color_picker=self.js_color_picker)
        self.js_ik_jnt_radius = components.float_field(self.js_frame_col, 'ik joint radius', 100, 135, value=0.2)

        self.js_fk_jnt_color = components.button_color_index_slider(self.js_frame_col, "fk joint", 100, 130, color_picker=self.js_color_picker)
        self.js_fk_jnt_radius = components.float_field(self.js_frame_col, 'fk joint radius', 100, 135, value=0.7)

        self.js_jnt_color = components.button_color_index_slider(self.js_frame_col, "joint color", 100, 130, color_picker=self.js_color_picker)
        self.js_jnt_radius = components.float_field(self.js_frame_col, 'joint radius', 100, 135, value=0.5)

        self.js_ik_cntrl_color = components.button_color_index_slider(self.js_frame_col, "ik cntrl color", 100, 130, color_picker=self.js_color_picker)
        self.js_fk_cntrl_color = components.button_color_index_slider(self.js_frame_col, "fk cntrl color", 100, 130, color_picker=self.js_color_picker)
        components.separator(self.js_frame_col)
        
        self.js_cb = components.check_box(self.js_frame_col, 'selection')
        #selection joint frame
        self.js_start_jnt = components.select_text_field(self.js_frame_col, 'start joint', 100, 135, long_name=True)
        self.js_end_jnt = components.select_text_field(self.js_frame_col, 'end joint', 100, 135, long_name=True)
        self.js_switch_cntrl = components.select_text_field(self.js_frame_col, 'switch cntrl', 100, 135, long_name=True)

        #checkbox update
        self.js_cb.on_update(
            on_function=lambda x: (self.js_start_jnt.editable(False),
                self.js_end_jnt.editable(False),
                self.js_switch_cntrl.editable(False)), 
            off_function=lambda y: (self.js_start_jnt.editable(True),
                self.js_end_jnt.editable(True),
                self.js_switch_cntrl.editable(True)))
        self.js_ik_name = components.text_field(self.js_frame_col, 'ik name', 100, 135)

        components.button(self.js_frame_col, 'build joint chain', lambda x: self.__joint_setup_function__())
    def __joint_setup_function__(self):
        #change it so the function also has color on it
        importlib.reload(object_lib)
        importlib.reload(joint_lib)
        ik_info = joint_lib.joint_info(color=self.js_ik_jnt_color.get_value() , radius=self.js_ik_jnt_radius.get_value())
        fk_info = joint_lib.joint_info(color=self.js_fk_jnt_color.get_value(), radius=self.js_fk_jnt_radius.get_value())
        jnt_info = joint_lib.joint_info(color=self.js_jnt_color.get_value(), radius=self.js_jnt_radius.get_value())

        #getting info for function
        start_jnt = 0
        end_jnt = 0
        switch_cntrl = 0
        if self.js_cb.get_value():
            sel = cmds.ls(sl=True, long=True)
            start_jnt = sel[0]
            end_jnt = sel[1]
            switch_cntrl = sel[2]
        else:
            start_jnt = self.js_start_jnt.get_value()[0]
            end_jnt = self.js_end_jnt.get_value()[0]
            switch_cntrl = self.js_switch_cntrl.get_value()[0]
        joint_lib.setup_jnt_chain(start_jnt, end_jnt, 
            self.js_ik_name.get_value()[0], switch_cntrl, ik_info, fk_info, jnt_info, self.js_ik_cntrl_color.get_value(), self.js_fk_cntrl_color.get_value())

