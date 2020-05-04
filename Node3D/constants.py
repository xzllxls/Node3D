WITH_CUDA = False
try:
    import cupy
    WITH_CUDA = True
except:
    import numpy as cupy


class NodeCategory(object):
    NONE = None
    GEOMETRY = 0
    CALCULATE = 1
    IMAGE = 2


class NodeMessageLevel(object):
    NONE = 0
    WARNING = 1
    ERROR = 2