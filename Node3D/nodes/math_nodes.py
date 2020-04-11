from Node3D.base.node import AutoNode, ModuleNode
from Node3D.base.node.module_node import get_functions_from_type
import numpy as np
from Node3D.vendor.NodeGraphQt.constants import *
import math


def add(x, y):
    return x + y


def sub(x, y):
    return x - y


def mul(x, y):
    return x * y


def div(x, y):
    return x / y


math.add = add
math.sub = sub
math.mul = mul
math.div = div


class MathModuleNode(ModuleNode):
    """
    Math functions node.
    """

    # set a unique node identifier.
    __identifier__ = 'Math'

    # set the initial default node name.
    NODE_NAME = 'Math Module'

    module_functions = get_functions_from_type(math)

    def __init__(self):
        super(MathModuleNode, self).__init__(float, float)
        self.defaultValue = 0.0


class DataViewerNode(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Data View'

    def __init__(self):
        super(DataViewerNode, self).__init__()
        self.add_input('in data')
        self.add_text_input('data', 'Data Viewer', multi_line=True)
        self.add_output("out")
        self.create_property("out", None)

    def run(self):
        value = self.get_input_data(0)
        if type(value) == float:
            self.set_property('data', "{:.10f}".format(value))
        else:
            self.set_property('data', str(value))
        self.set_property('out', value)


class Time(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Time'

    def __init__(self):
        super(Time, self).__init__()
        self.add_output("Frame", int)
        self.add_output("Time", float)
        self.create_property("Frame", 0)
        self.create_property("Time", 0.0)

    def set_graph(self, graph):
        super(Time, self).set_graph(graph)
        self.graph.master.timeline.frameChanged.connect(self.tick)

    def tick(self, frame):
        self.set_property("Frame", frame)
        self.set_property("Time", float(frame) / self.graph.master.timeline.fps)
        self.cookNextNode()


class Sin(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Sin'

    def __init__(self):
        super(Sin, self).__init__()
        self.add_output('out', np.ndarray)
        self.create_property('out', None)
        self.add_input('data', np.ndarray)

    def run(self):
        data = self.get_input_data(0)
        if data is None:
            self.error("No enough input")
            return
        self.set_property('out', np.sin(data))


class Add(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Add'

    def __init__(self):
        super(Add, self).__init__()
        self.add_output('out', np.ndarray)
        self.create_property('out', None)
        self.add_input('A', np.ndarray)
        self.add_input('B', None)

    def run(self):
        a = self.get_input_data(0)
        b = self.get_input_data(1)

        if a is None or b is None:
            self.error("No enough input")
            return
        self.set_property('out', np.add(a, b))


class Subtract(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Subtract'

    def __init__(self):
        super(Subtract, self).__init__()
        self.add_output('out', np.ndarray)
        self.create_property('out', None)
        self.add_input('A', np.ndarray)
        self.add_input('B', None)

    def run(self):
        a = self.get_input_data(0)
        b = self.get_input_data(1)

        if a is None or b is None:
            self.error("No enough input")
            return
        self.set_property('out', np.subtract(a, b))


class Multiply(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Multiply'

    def __init__(self):
        super(Multiply, self).__init__()
        self.add_output('out', np.ndarray)
        self.create_property('out', None)
        self.add_input('A', np.ndarray)
        self.add_input('B', None)

    def run(self):
        a = self.get_input_data(0)
        b = self.get_input_data(1)

        if a is None or b is None:
            self.error("No enough input")
            return
        self.set_property('out', np.multiply(a, b))


class Divide(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Divide'

    def __init__(self):
        super(Divide, self).__init__()
        self.add_output('out', np.ndarray)
        self.create_property('out', None)
        self.add_input('A', np.ndarray)
        self.add_input('B', None)

    def run(self):
        a = self.get_input_data(0)
        b = self.get_input_data(1)

        if a is None or b is None:
            self.error("No enough input")
            return
        self.set_property('out', np.divide(a, b))


class Random(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Random'

    def __init__(self):
        super(Random, self).__init__()
        self.add_output('out', np.ndarray)
        self.create_property('out', None)
        self.add_input('data', np.ndarray)

    def run(self):
        a = self.get_input_data(0)
        if a is None:
            self.error("No enough input")
            return
        self.set_property('out', np.random.random(a.shape))


class VectorSplit(AutoNode):
    """
    Splict a vector to x,y,z
    """

    __identifier__ = 'Math'
    NODE_NAME = 'Vector Split'

    def __init__(self):
        super(VectorSplit, self).__init__()

        self.add_output('x')
        self.create_property("x", 0.0)
        self.add_output('y')
        self.create_property("y", 0.0)
        self.add_output('z')
        self.create_property("z", 0.0)
        self.add_output('w')
        self.create_property("w", 0.0)

        self.add_input("in vector", list)
        self.map = {0: "x", 1: "y", 2: "z", 3: "w"}

    def run(self):
        value = self.get_input_data(0)
        if type(value) is not list:
            self.error("Input data not list")
        for index, data in enumerate(value):
            if index > 3:
                return
            self.set_property(self.map[index], data)


class VectorMaker(AutoNode):
    """
    Create a vector by three float value
    """

    __identifier__ = 'Math'
    NODE_NAME = 'Vector Maker'

    def __init__(self):
        super(VectorMaker, self).__init__()

        self.add_output('out', list)
        self.create_property("out", None)

        self.add_input("x", float)
        self.add_input("y", float)
        self.add_input("z", float)
        self.add_input("w", float)

    def run(self):
        result = []
        for i in range(4):
            data = self.get_input_data(i)
            if data is not None:
                result.append(data)

        self.set_property("out", result)


class DataConvect(AutoNode):
    """
    Create a vector by three float value
    """

    __identifier__ = 'Math'
    NODE_NAME = 'Data Convect'

    def __init__(self):
        super(DataConvect, self).__init__()

        self.add_output('out')
        self.create_property("out", None)
        self.add_input("in data")

        items = ["all to int", "all to float", "all to string", "eval string", "all to list"]
        self.add_combo_menu('method', 'Method', items=items)

    def run(self):
        method = self.get_property("method")
        try:
            if method == "all to int":
                data = int(float(self.get_input_data(0)))
            elif method == "all to float":
                data = float(self.get_input_data(0))
            elif method == "all to string":
                data = str(self.get_input_data(0))
            elif method == "eval string":
                data = eval(self.get_input_data(0))
            elif method == "all to list":
                data = list(self.get_input_data(0))
            self.set_property("out", data)
        except Exception as error:
            self.error(error)


class FloatInputNode(AutoNode):
    """
    Input float data.
    """

    __identifier__ = 'Math'
    NODE_NAME = 'Float'

    def __init__(self):
        super(FloatInputNode, self).__init__()
        self.output = self.add_output('out', float)
        self.add_float_input('out', 'Float Value', value=0.0, range=(-10, 10))


class IntInputNode(AutoNode):
    """
    Input int data.
    """

    __identifier__ = 'Math'
    NODE_NAME = 'Int'

    def __init__(self):
        super(IntInputNode, self).__init__()
        self.output = self.add_output('out', int)
        self.add_int_input('out', 'Int Value', value=0)


class Vector2InputNode(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Vector2'

    def __init__(self):
        super(Vector2InputNode, self).__init__()
        self.output = self.add_output('out', list)
        self.create_property(
            "out", [0.0, 0.0], widget_type=NODE_PROP_VECTOR2)


class Vector3InputNode(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Vector3'

    def __init__(self):
        super(Vector3InputNode, self).__init__()
        self.output = self.add_output('out', list)
        self.create_property(
            "out", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)


class Vector4InputNode(AutoNode):
    __identifier__ = 'Math'
    NODE_NAME = 'Vector4'

    def __init__(self):
        super(Vector4InputNode, self).__init__()
        self.output = self.add_output('out', list)
        self.create_property(
            "out", [0.0, 0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR4)


class BoolInputNode(AutoNode):
    """
    Input Bool data.
    """

    __identifier__ = 'Math'
    NODE_NAME = 'Bool'

    def __init__(self):
        super(BoolInputNode, self).__init__()
        self.add_output('out', bool)
        self.create_property('out', True)
        self.add_combo_menu('combo', 'Bool value', items=['True', 'False'])

    def run(self):
        self.set_property('out', eval(self.get_property('combo')))


class IfNode(AutoNode):
    """
    if node.
    """

    __identifier__ = 'Math'
    NODE_NAME = 'If'

    def __init__(self):
        super(IfNode, self).__init__()
        self.condition = self.add_input('condition')
        self._then = self.add_input('then')
        self._else = self.add_input('else')
        self.add_output('out')
        self.create_property('out', None)

    def run(self):
        if self.get_input_data(self.condition):
            result = self.get_input_data(self._then)
        else:
            result = self.get_input_data(self._else)

        self.set_property('out', result)


class BooleanNode(AutoNode):
    """
    Boolean Logic funtions node.
    """

    __identifier__ = 'Math'

    NODE_NAME = 'Boolean'

    logics = {'and': 'a and b',
              'or': 'a or b',
              'xor': '(not a and b) or (a and not b)',
              'not': 'not a'}

    def __init__(self):
        super(BooleanNode, self).__init__()
        self.a = self.add_input('a', bool)
        self.b = self.add_input('b', bool)
        self.add_output('out', bool)
        self.create_property('out', None)
        self.add_combo_menu('funcs',
                            'Functions',
                            items=list(self.logics.keys()),
                            tab='widgets')

        self.func = self.logics['and']
        # switch math function type
        self.view.widgets['funcs'].value_changed.connect(self.addFunction)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = self.logics[func]
        if self.b.visible() and not 'b' in self.func:
            self.b.set_visible(False)
        elif not self.b.visible():
            self.b.set_visible(True)
        self.cook()

    def run(self):
        a = self.get_input_data(self.a)
        b = self.get_input_data(self.b)

        if a is None or (b is None and 'b' in self.func):
            self.error("No inputs!")
            return

        self.set_property('out', eval(self.func))
