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
        self.add_combo_menu("Group Class", "Group Class", items=['vertex', 'edge', 'face'])
        self.add_combo_menu("Group Name", "Group Name", items=['No Group'])
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        group_class = self.get_property('Group Class')

        items = ['No Group']
        items.extend(self.geo.getGroupNames()[group_class])
        self.update_combo_menu('Group Name', items)

        group_name = self.get_property('Group Name')
        if group_name == 'No Group':
            return

        self.geo.removeGroup(group_class, group_name)


class Group_Create(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Create'

    def __init__(self):
        super(Group_Create, self).__init__()
        self.add_combo_menu("Group Class", "Group Class", items=['vertex', 'edge', 'face'])
        self.add_text_input("Group Name", "Group Name", '')
        self.add_input("geo", GeometryNode)
        self.add_checkbox("Group Value", "Group Value", state=False)

    def run(self):
        if not self.copyData():
            return
        group_name = self.get_property('Group Name')
        if len(group_name) == 0:
            return

        value = self.get_property('Group Value')
        group_class = self.get_property('Group Class')

        self.geo.createGroup(group_class,group_name,value)


class Group_Promote(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Promote'

    def __init__(self):
        super(Group_Promote, self).__init__()
        self.add_combo_menu("From", "From", items=['vertex', 'edge', 'face'])
        self.add_combo_menu("To", "To", items=['vertex', 'edge', 'face'])
        self.add_combo_menu("Group Name", "Group Name", items=['No Group'])
        self.add_text_input("New Group Name", "New Group Name", "")
        self.add_checkbox("Delete Origin", "Delete Origin", state=False)
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        from_class = self.get_property('From')
        to_class = self.get_property('To')

        items = ['No Group']
        items.extend(self.geo.getGroupNames()[from_class])
        self.update_combo_menu('Group Name', items)
        group_name = self.get_property('Group Name')
        if group_name == 'No Group':
            return

        new_name = get_group_name(to_class, self.get_property('New Group Name'))
        group_name = get_group_name(from_class, group_name)

        if new_name == "":
            return

        if from_class == 'vertex':
            if to_class == 'face':
                self.geo.meshFuncs.VertexToFace(group_name, new_name)
            elif to_class == 'edge':
                self.geo.meshFuncs.VertexToEdge(group_name, new_name)
            elif to_class == 'vertex':
                if group_name != new_name:
                    self.geo.meshFuncs.attribCopy('vertex', group_name, new_name)
        elif from_class == 'face':
            if to_class == 'vertex':
                self.geo.meshFuncs.FaceToVertex(group_name, new_name)
            elif to_class == 'face':
                if group_name != new_name:
                    self.geo.meshFuncs.attribCopy('face', group_name, new_name)
        elif from_class == 'edge':
            if to_class == 'vertex':
                self.geo.meshFuncs.EdgeToVertex(group_name, new_name)
            elif to_class == 'edge':
                if group_name != new_name:
                    self.geo.meshFuncs.attribCopy('edge', group_name, new_name)

        if self.get_property("Delete Origin"):
            self.geo.removeAttribute(from_class, group_name)


class Group_Rename(GeometryNode):
    __identifier__ = 'Group'
    NODE_NAME = 'Group_Rename'

    def __init__(self):
        super(Group_Rename, self).__init__()
        self.add_combo_menu("Group Class", "Group Class", items=['vertex', 'edge', 'face'])
        self.add_combo_menu("Group Name", "Group Name", items=['No Group'])
        self.add_text_input("New Group Name", "New Group Name", "")
        self.add_input("geo", GeometryNode)

    def run(self):
        if not self.copyData():
            return

        group_class = self.get_property('Group Class')

        items = ['No Group']
        items.extend(self.geo.getGroupNames()[group_class])
        self.update_combo_menu('Group Name', items)

        group_name = self.get_property('Group Name')
        if group_name == 'No Group':
            return

        new_name = self.get_property('New Group Name')

        if new_name == "":
            return

        self.geo.renameAttribute(group_class, get_group_name(group_class, group_name),
                                 get_group_name(group_class, new_name))