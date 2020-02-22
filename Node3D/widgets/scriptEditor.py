from ..vendor.ScriptEditor.scriptEditor import scriptEditor
from ..base.node.script_node import ScriptNode


class nodeScriptEditor(scriptEditor):
    def __init__(self):
        super(nodeScriptEditor, self).__init__()
        self.node = None
        self.edit = None
        self.createNodeTab()

    def getNodeTab(self):
        if self.edit is None:
            for i in range(self.tab.count()):
                text = self.tab.tabText(i)
                if text == 'NodeScript':
                    self.edit = self.tab.widget(i).edit
                    self.edit.saveSignal.connect(self.update_node)

    def createNodeTab(self):
        self.getNodeTab()
        if self.edit is not None:
            return
        self.edit = self.tab.addNewTab('NodeScript')
        self.edit.saveSignal.connect(self.update_node)

    def set_node(self, node):
        if not isinstance(node, ScriptNode):
            return
        if self.node:
            if node.id != self.node.id:
                self.node = node
            else:
                return
        else:
            self.node = node

        self.createNodeTab()
        self.edit.setText(self.node.get_property('Script'))

    def update_node(self):
        if self.node is not None:
            self.node.set_property('Script', self.edit.toPlainText())

        # self.clear_MeshItems()
        # if self.node and self.node.geo:
        #     self.addMeshItem(self.node.geo)
        # self.update()