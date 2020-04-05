### About Node3D ###

**Node3D** is a node-based 3D application developed with Python. The project is focusing on procedural 3D data processing and interactive user interface.
**Node3D** is an open-source project under MIT license.

### Requirements ###

Node3D requires the following environment.

* [Python](https://www.python.org/) v3.7.4 or higher.

The following libraries can be installed with `pip`.
* [PySide2](https://pypi.org/project/PySide2/) v5.14 or higher
* [Qt.py](https://pypi.org/project/Qt.py/) v1.2.4 or higher
* [PyOpenGL](https://pypi.org/project/PyOpenGL/) v3.1.5 or higher
* [QDarkStyle](https://pypi.org/project/QDarkStyle/) v2.8 or higher
* [numpy](https://pypi.org/project/numpy/) v1.18.2 or higher
* [scipy](https://pypi.org/project/scipy/) v1.4.1 or higher
* [numba](http://numba.pydata.org/) v0.48.0 or higher
* [numpy-quaternion](https://pypi.org/project/numpy-quaternion/)
* [pyfastnoisesimd](https://github.com/robbmcleod/pyfastnoisesimd)

The following library requires pre-compiled `whl`
* [openmesh-python](https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python)

The followings are optional dependencies, and need to be compiled from source code:
* [pyassimp](https://github.com/assimp/assimp/blob/master/port/PyAssimp/README.md)
* [open3d](https://github.com/intel-isl/Open3D)
* [igl](https://github.com/libigl/libigl-python-bindings)
* [CGAL](https://github.com/CGAL/cgal-swig-bindings)

The following third-party libraries which has been modified are already included in `vendor` directory.
* [NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt)
* [pw_MultiScriptEditor](https://github.com/paulwinex/pw_MultiScriptEditor)
* [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph)
