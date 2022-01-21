import maya.cmds as cmds

def load_sel(text_field, long=False):
    sel=cmds.ls(sl=True, long=long)
    if len(sel) > 0:
        cmds.textField(text_field, e=True, text=', '.join(sel))
def resize_frame_layout(window, frame_layout, height, expand=False):
    if not expand:
        window_height = cmds.window(window, query=True, height=True)
        frame_height=cmds.frameLayout(frame_layout, query=True, height=True)
        cmds.window(window, edit=True, height=window_height - height + 25)
        cmds.frameLayout(frame_layout, edit=True, height= 25)
    else:
        window_height = cmds.window(window, query=True, height=True)
        frame_height = cmds.frameLayout(frame_layout, query=True, height=True)
        cmds.window(window, edit=True, height=window_height + height - 25)
        cmds.frameLayout(frame_layout, edit=True, height=frame_height + height - 25)
def get_UI_parent_string(obj):
    if hasattr(obj, "get_name"):
        return obj.get_name()
    return obj