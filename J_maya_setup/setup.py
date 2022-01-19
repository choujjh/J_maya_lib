import maya.cmds as cmds
import os
import shutil

class J_maya_lib_setup():
    def __init__(self):
        self.name = 'startup'
        self.script_dir = cmds.internalVar(userScriptDir=True)
        self.setup_path = os.path.dirname(__file__)
        print(self.script_dir)
        print(self.setup_path)

# shutil.move(, )
#cmds.quit()
