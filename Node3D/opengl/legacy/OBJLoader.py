import numpy as np


class OBJLoader(object):
    def __init__(self, file=None):
        self.file = file
        self._vertices = []
        self._normals = []
        self._uvs = []
        self.faces = []

        self.vertices = []
        self.normals = []
        self.uvs = []

        self.face_normals = []
        self.face_uvs = []
        self.face_vertices = []

        self.hasface = False

    @staticmethod
    def Load(file):
        if not file.lower().endswith(".obj"):
            return "Not OBJ File"

        reader = OBJLoader(file)
        with open(file, 'rb') as f:
            line = f.readline().decode('ascii', 'ignore')
            while line:
                line = line.strip()
                reader.readLine(line)
                line = f.readline().decode('ascii', 'ignore')

        reader.post_process()
        return reader

    def readLine(self, line):
        if line.startswith('v '):
            self._vertices.append(self.readTuple(line))
        elif line.startswith('vt '):
            self._uvs.append(self.readTuple(line))
        elif line.startswith('vn '):
            self._normals.append(self.readTuple(line))
        elif line.startswith('f '):
            if not self.hasface:
                self.hasface = True
            if "/" in line:
                self.readData(self.readTuple(line))
            else:
                self.readFace(self.readTuple(line))
        elif any(line.startswith(x) for x in ('g', 's', 'o', 'usemtl')):
            pass  # Ignore groups and smoothing groups, obj names, material
        else:
            pass

    def readTuple(self, line):
        values = [num for num in line.split(' ') if num]
        return values[1:]

    def readFace(self, d):
        # d: face : [100 254 34]

        self.face_vertices.extend([d[0], d[1], d[2]])
        if len(d) == 4:
            self.face_vertices.extend([d[2], d[3], d[0]])

    def readData(self, datas):
        # datas: f : [100/24/23, 254/35/485, 34/234/354]
        #            vertex/texcoord/normal
        d = []
        for data in datas:
            d.append(data.split("/"))

        # d: f : [[100,24,23], [254,35,485], [34,234,354]]

        num = len(d[0])

        if len(d[0][0]) > 0:
            self.face_vertices.extend([d[0][0], d[1][0], d[2][0]])
        if len(d[0][1]) > 0:
            self.face_uvs.extend([d[0][1], d[1][1], d[2][1]])
        if num >= 3:
            if len(d[0][2]) > 0:
                self.face_normals.extend([d[0][2], d[1][2], d[2][2]])

        if len(datas) == 4:
            if len(d[0][0]) > 0:
                self.face_vertices.extend([d[2][0], d[3][0], d[0][0]])
            if len(d[0][1]) > 0:
                self.face_uvs.extend([d[2][1], d[3][1], d[0][1]])
            if num >= 3:
                if len(d[0][2]) > 0:
                    self.face_normals.extend([d[2][2], d[3][2], d[0][2]])

    def post_process(self):
        if not self.face_vertices:
            if self._vertices:
                self.vertices = np.array(self._vertices, dtype=np.float32)
            else:
                self.vertices = None
        else:
            _vertices = np.array(self._vertices, dtype=np.float32)
            face_vertices = np.array(self.face_vertices, dtype=np.uint32)
            self.vertices = _vertices[face_vertices - 1]

        if not self.face_normals:
            if self._normals:
                self.normals = np.array(self._normals, dtype=np.float32)
            else:
                self.normals = None
        else:
            _normals = np.array(self._normals, dtype=np.float32)
            face_normals = np.array(self.face_normals, dtype=np.uint32)
            self.normals = _normals[face_normals - 1]

        if not self.face_uvs:
            if self._uvs:
                self.uvs = np.array(self._uvs, dtype=np.float32)
            else:
                self.uvs = None
        else:
            _uvs = np.array(self._uvs, dtype=np.float32)
            face_uvs = np.array(self.face_uvs, dtype=np.uint32)
            self.uvs = _uvs[face_uvs - 1]

        if self.hasface:
            num = self.vertices.shape[0]
            self.faces = np.arange(0, num, 1, dtype=np.uint32)
            self.faces = self.faces.reshape(int(num / 3), 3)
        else:
            self.faces = None

