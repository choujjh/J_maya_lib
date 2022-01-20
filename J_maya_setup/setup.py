import maya.cmds as cmds
import os
import shutil

class J_maya_lib_setup():
    def __init__(self):
        self.name = 'startup'
        self.script_dir = cmds.internalVar(userScriptDir=True)
        self.setup_path = os.path.dirname(__file__)
        #if file to be moved does exist
        if os.path.exists('{}/userSetup.py'.format(self.setup_path)):
            #if userSetup doesn't exist
            if not os.path.exists('{}/userSetup.py'.format(self.script_dir)):
                shutil.move('{}/userSetup.py'.format(self.setup_path), '{}/userSetup.py'.format(self.script_dir))
            else:
                print('file already used')
        print(self.script_dir)
        print(self.setup_path)

# TODO: install the shelf tools
#cmds.quit()
