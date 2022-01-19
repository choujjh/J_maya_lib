import maya.cmds as cmds
import os
from filecmp import cmp
import shutil

class J_maya_lib_setup():
    def __init__(self):
        self.name = 'startup'
        self.script_dir = cmds.internalVar(userScriptDir=True)
        self.setup_path = os.path.dirname(__file__)
        #if file to be moved does exist
        source = '{}/userSetup.py'.format(self.setup_path)
        destination = '{}/userSetup.py'.format(self.script_dir)
        if os.path.exists(source):
            #if userSetup doesn't exist
            if not os.path.exists(destination):
                shutil.copy(source, destination)
                #quit here
            else:
                if not cmp(source, destination):
                    cmds.warning('{} file already exists'.format(destination))
                else:
                    print('files are the same, no changes made')

# shutil.move(, )
#cmds.quit()
