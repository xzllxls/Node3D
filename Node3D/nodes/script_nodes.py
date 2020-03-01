from Node3D.base.node import ScriptNode
from Node3D.opengl import Mesh
import numba
from collections import namedtuple
import traceback


class Python(ScriptNode):
    __identifier__ = 'Script'
    NODE_NAME = 'Python'

    def __init__(self):
        super(Python, self).__init__()

    def execute(self):
        if self.namespace['gp'] is None:
            self.namespace['gp'] = self.graph
        try:
            exec(self.get_property('Script').strip(), self.namespace)
        except:
            self.error(traceback.format_exc())

    def run(self):
        if not self.copyData():
            self.geo = Mesh()

        self.execute()


class Vertex_Wrangle(ScriptNode):
    __identifier__ = 'Script'
    NODE_NAME = 'Vertex_Wrangle'

    def __init__(self):
        super(Vertex_Wrangle, self).__init__()
        # attribs = {}
        self.preCode = '''def run_per_vertex({}, _vertex_count):
    for idx in range(_vertex_count):
        pass
'''
        self.func = None

    def getAllVertexAttributes(self):
        dt = self.get_property('Depend Time')
        names = list(self.geo.detailAttribute["vertex"].keys())

        data = []
        for attrib_name in names:
            try:
                d = self.geo.getVertexAttribData(attrib_name, True)
            except:
                d = self.geo.getVertexAttribData(attrib_name)
            data.append(d)
        if dt:
            data.append(self.getFrame())
        data.append(self.geo.getNumVertexes())
        return data

    def getPreCode(self):
        dt = self.get_property('Depend Time')
        names = list(self.geo.detailAttribute["vertex"].keys())
        if dt:
            names.append('Frame')
        lts = ','.join(names)
        # pss = ""
        # for n in names:
        #     pss += "'{0}':{0},".format(n)
        # pss = '{' + pss + '}'
        return self.preCode.format(lts)

    def updateCode(self):
        if self.geo is None:
            return
        preCode = self.getPreCode()
        lines = self.get_property('Script').strip()
        lines = preCode + '\n'.join('        ' + line for line in lines.splitlines())
        if self.namespace['gp'] is None:
            self.namespace['gp'] = self.graph
        exec(lines, self.namespace)
        self.func = numba.jit(nopython=True, nogil=True, parallel=True)(self.namespace['run_per_vertex'])

    def set_property(self, name, value):
        super().set_property(name, value)
        if name == 'Script' or name == 'Depend Time':
            self.updateCode()
            self.cook()

    def execute(self):
        data = self.getAllVertexAttributes()
        if self.func is None:
            self.updateCode()
        try:
            self.func(*data)
        except:
            self.error(traceback.format_exc())

    def run(self):
        if not self.copyData():
            self.geo = None
            return

        self.execute()