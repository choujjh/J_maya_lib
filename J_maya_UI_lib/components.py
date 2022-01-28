from J_maya_lib.J_maya_UI_lib import UI_helpers
from J_maya_lib.J_maya_helper_lib import helpers

import maya.cmds as cmds

import importlib

importlib.reload(UI_helpers)
importlib.reload(helpers)

#visibility
#on change
#parent
#return name
#on update
#get value


class text_field:
    def __init__(self, parent, tx_label, tx_width=0, long_name=False):
        if tx_width == 0:
            tx_width = len(tx_label * 8)
        self.layout = cmds.rowColumnLayout(nc = 2, columnWidth=[(1, tx_width)], p=UI_helpers.get_UI_parent_string(parent))
        self.text = cmds.text(l = tx_label)
        self.tf = cmds.textField()
    #changing things on text_field
    def set_vis(self, visibility):
        cmds.text(self.text, e=True, visible=visibility)
        cmds.textField(self.tf, e=True, visible=visibility)
    def editable(self, edit):
        cmds.text(self.text, e=True, en=edit)
        cmds.textField(self.tf, e=True, ed=edit, en=edit)
    #getting information from class
    def get_name(self):
        return self.layout
    def get_value(self):
        return cmds.textField(self.tf, q=True, text=True).split(', ')

class select_text_field:
    def __init__(self, parent, b_label, b_width=0, long_name=False):
        if b_width == 0:
            b_width = len(b_label * 8)
        self.layout = cmds.rowColumnLayout(nc = 2, columnWidth=[(1, b_width)], p=UI_helpers.get_UI_parent_string(parent))
        self.button = cmds.button(l = b_label)
        self.tf = cmds.textField()
        cmds.button(self.button, e=True, c = lambda x: UI_helpers.load_sel(self.tf, long=long_name))
    #changing things on palette port
    def set_vis(self, visibility):
        cmds.button(self.button, e=True, visible=visibility)
        cmds.textField(self.tf, e=True, visible=visibility)
    def editable(self, edit):
        cmds.button(self.button, e=True, en=edit)
        cmds.textField(self.tf, e=True, ed=edit, en=edit)
    def get_name(self):
        return self.layout
    def get_value(self):
        val = cmds.textField(self.tf, q=True, text=True)
        if val == '':
            return []
        else:
            return val.split(', ')
    
class radio_collection:
    def __init__(self, parent, button_names, columns=None, verticle=True, select_index=0):
        button_names = helpers.turn_to_list(button_names)
        self.layout = '..'
        if verticle:
            self.layout = cmds.columnLayout(p=UI_helpers.get_UI_parent_string(parent))
        else:
            if columns==None:
                columns= len(button_names)
            self.layout = cmds.rowColumnLayout(nc = columns, p=UI_helpers.get_UI_parent_string(parent))
        self.name = cmds.radioCollection(p=self.layout)
        self.rad_buttons = []
        for rb in button_names:
            self.rad_buttons.append(cmds.radioButton(label=rb, p=self.layout))
        cmds.radioCollection(self.name, e=True, sl=self.rad_buttons[select_index])
    def on_update(self, function):
        if function != None:
            for rb in self.rad_buttons:
                cmds.radioButton(rb, edit=True, cc=function)
    def get_name(self):
        return self.name
    def get_value(self):
        try:
            rb = cmds.radioCollection(self.name, q=True, sl=True)
            return cmds.radioButton(rb, q=True, label=True)
        except:
            cmds.warning('radio button not selected')
    def get_rad_button_fields(self):
        return self.rad_buttons

class color_picker:
    def __init__(self, parent, width=400, height=120, visibility=True, edit=True):
        self.name = palette = cmds.palettePort(dim=(12, 3), topDown=True, vis=True, scc=16, p=UI_helpers.get_UI_parent_string(parent))
        for i in range(1, 37):
            if i <= 31:
                temp = cmds.colorIndex(i, q=True)
                cmds.palettePort(palette, rgb = [i-1, temp[0], temp[1], temp[2]], e=True, r=True)
            else:
                cmds.palettePort(palette, rgb = [i-1, 0, 0, 0], e=True, r=True)
        self.set_width_height(width, height)
        self.set_vis(visibility)
        self.editable(edit)
    #changing things on palette port
    def set_vis(self, visibility):
        cmds.palettePort(self.name, e=True, visible=visibility)
    def editable(self, edit):
        cmds.palettePort(self.name, e=True, ed=edit)
    def set_width_height(self, width, height):
        width = cmds.palettePort(self.name, e=True, w=width, h=height)
    
    #getting information from class
    def get_name(self):
        return self.name
    # def get_width_height(self):
    #     width = cmds.palettePort(self.name, q=True, w=True)
    #     height = cmds.palettePort(self.name, q=True, h=True)
    #     return width, height
    def get_value(self):
        return cmds.palettePort(self.name, q=True, scc=True) + 1
    
class check_box:
    def __init__(self, parent, label):
        self.cb = cmds.checkBox(label=label, p=parent)
        
    def set_vis(self, visibility):
        cmds.checkBox(self.cb, e=True, visible=visibility)
    def editable(self, edit):
        cmds.checkBox(self.cb, e=True, ed=edit)
    def on_update(self, on_function=None, off_function=None):
        if on_function != None:
            cmds.checkBox(self.cb, e=True, onCommand=on_function)
        if off_function != None:
            cmds.checkBox(self.cb, e=True, offCommand=off_function)

    #getting information from class
    def get_name(self):
        return self.cb
    def get_value(self):
        return cmds.checkBox(self.cb, q=True, v=True)
