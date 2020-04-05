from Node3D.base.node import GeometryNode
import numpy as np


def get_group_name(group_class, name):
    if group_class == 'vertex':
        name = "v:" + name
    elif group_class == 'face':
        name = "f:" + name
    elif group_class == 'edge':
        name = "e:" + name
    return name


class Group_Delete(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Delete'

    def __init__(self):
        super(Group_Delete, self).__init__()
        self.add_input("geo", GeometryNode)
        self.set_parameters(
            [{'name': 'Group Class', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face']},
             {'name': 'Group Name', 'type': 'listText'}])

    def run(self):
        if not self.copyData():
            return

        group_class = self.get_property('Group Class')
        self.update_list_text_param('Group Name', self.geo.getGroupNames()[group_class])
        group_name = self.get_property('Group Name')
        if not self.geo.hasGroup(group_class, group_name):
            return

        self.geo.removeGroup(group_class, group_name)


class Group_Create(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Create'

    def __init__(self):
        super(Group_Create, self).__init__()
        self.add_input("geo", GeometryNode)
        self.set_parameters(
            [{'name': 'Group Class', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face']},
             {'name': 'Group Name', 'type': 'str'},
             {'name': 'Group Value', 'type': 'bool', 'value': False}])

    def run(self):
        if not self.copyData():
            return
        group_name = self.get_property('Group Name')
        if not group_name:
            return

        value = self.get_property('Group Value')
        group_class = self.get_property('Group Class')

        self.geo.createGroup(group_class, group_name, value)


class Group_Promote(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Promote'

    def __init__(self):
        super(Group_Promote, self).__init__()
        self.add_input("geo", GeometryNode)
        self.set_parameters(
            [{'name': 'From', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face']},
             {'name': 'To', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face']},
             {'name': 'Group Name', 'type': 'listText'},
             {'name': 'New Group Name', 'type': 'str'},
             {'name': 'Delete Origin', 'type': 'bool', 'value': True}])

    def run(self):
        if not self.copyData():
            return

        from_class = self.get_property('From')
        to_class = self.get_property('To')

        self.update_list_text_param('Group Name', self.geo.getGroupNames()[from_class])
        group_name = self.get_property('Group Name')
        if not self.geo.hasGroup(from_class, group_name):
            return

        new_name = get_group_name(to_class, self.get_property('New Group Name'))
        group_name = get_group_name(from_class, group_name)

        if not new_name:
            return

        if from_class == 'vertex':
            if to_class == 'face':
                self.geo.meshFuncs.VertexToFace(group_name, new_name)
            elif to_class == 'edge':
                self.geo.meshFuncs.VertexToEdge(group_name, new_name)
            elif to_class == 'vertex':
                if group_name != new_name:
                    self.geo.copyAttribute('vertex', group_name, new_name)
        elif from_class == 'face':
            if to_class == 'vertex':
                self.geo.meshFuncs.FaceToVertex(group_name, new_name)
            elif to_class == 'face':
                if group_name != new_name:
                    self.geo.copyAttribute('face', group_name, new_name)
        elif from_class == 'edge':
            if to_class == 'vertex':
                self.geo.meshFuncs.EdgeToVertex(group_name, new_name)
            elif to_class == 'edge':
                if group_name != new_name:
                    self.geo.copyAttribute('edge', group_name, new_name)

        if self.get_property("Delete Origin"):
            self.geo.removeAttribute(from_class, group_name)


class Group_Rename(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Rename'

    def __init__(self):
        super(Group_Rename, self).__init__()
        self.add_input("geo", GeometryNode)
        self.set_parameters(
            [{'name': 'Group Class', 'type': 'list', 'value': 'vertex', 'limits': ['vertex', 'edge', 'face']},
             {'name': 'Group Name', 'type': 'listText'},
             {'name': 'New Group Name', 'type': 'str'}])

    def run(self):
        if not self.copyData():
            return

        group_class = self.get_property('Group Class')

        self.update_list_text_param('Group Name', self.geo.getGroupNames()[group_class])
        group_name = self.get_property('Group Name')
        if not self.geo.hasGroup(group_class, group_name):
            return

        new_name = self.get_property('New Group Name')

        if not new_name:
            return

        self.geo.renameAttribute(group_class, get_group_name(group_class, group_name),
                                 get_group_name(group_class, new_name))
