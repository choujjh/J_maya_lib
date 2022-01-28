


#frameLayout
#columnLayout
#rowLayout
#rowColumnLayout

#use decorator pattern

class layout:
    def __init__(self, parent):
        self.parent = parent
        self.children = []
    def get_width_height(self):
        print('width, height')
