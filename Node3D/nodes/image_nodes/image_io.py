from Node3D.base.node import ImageNode
from Node3D.constants import NodeCategory
import cv2, os
imports = ['exr', 'png', 'jpg', 'jpeg', 'tif', 'tiff', 'tga']


class File(ImageNode):
    # set a unique node identifier.
    __identifier__ = 'IO'

    # set the initial default node name.
    NODE_NAME = 'File Import'
    NODE_CATEGORY = NodeCategory.IMAGE

    def __init__(self):
        super(File, self).__init__()
        ext = "*." + ";*.".join(imports)
        self.add_file_input("file", "file", ext=ext)

    def run(self):
        self.image = None
        file_path = self.get_property('file')
        if not os.path.exists(file_path):
            return

        self.image = cv2.imread(file_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image = self.image.transpose((1, 0, 2)) / 255.0
