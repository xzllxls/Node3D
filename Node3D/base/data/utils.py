import numpy as np
from math import sqrt

# epsilon for testing whether a number is close to zero
_EPS = np.finfo(float).eps * 4.0

# axis sequences for Euler angles
_NEXT_AXIS = [1, 2, 0, 1]

# map axes strings to/from tuples of inner axis, parity, repetition, frame
_AXES2TUPLE = {
    'sxyz': (0, 0, 0, 0), 'sxyx': (0, 0, 1, 0), 'sxzy': (0, 1, 0, 0),
    'sxzx': (0, 1, 1, 0), 'syzx': (1, 0, 0, 0), 'syzy': (1, 0, 1, 0),
    'syxz': (1, 1, 0, 0), 'syxy': (1, 1, 1, 0), 'szxy': (2, 0, 0, 0),
    'szxz': (2, 0, 1, 0), 'szyx': (2, 1, 0, 0), 'szyz': (2, 1, 1, 0),
    'rzyx': (0, 0, 0, 1), 'rxyx': (0, 0, 1, 1), 'ryzx': (0, 1, 0, 1),
    'rxzx': (0, 1, 1, 1), 'rxzy': (1, 0, 0, 1), 'ryzy': (1, 0, 1, 1),
    'rzxy': (1, 1, 0, 1), 'ryxy': (1, 1, 1, 1), 'ryxz': (2, 0, 0, 1),
    'rzxz': (2, 0, 1, 1), 'rxyz': (2, 1, 0, 1), 'rzyz': (2, 1, 1, 1)}

_TUPLE2AXES = dict((v, k) for k, v in _AXES2TUPLE.items())


def vector_norm(data):
    """
    Return length of numpy vector
    """
    data = np.array(data, dtype=np.float64, copy=True)
    return sqrt(np.dot(data, data))


def unit_vector(data):
    """
    Return ndarray normalized by length
    """
    data = np.array(data, dtype=np.float64, copy=True)
    if data.ndim == 1:
        data /= sqrt(np.dot(data, data))
        return data


def AABB_Hit(bbox_min, bbox_max, origin, dir, ray_min=0.001, ray_max=1000000.0):
    if bbox_min[0] >= bbox_max[0] or bbox_min[0] >= bbox_max[0] or bbox_min[0] >= bbox_max[0]:
        return False
    for i in range(3):
        invD = 1.0 / dir[i]
        t0 = (bbox_min[i] - origin[i]) * invD
        t1 = (bbox_max[i] - origin[i]) * invD
        if invD < 0:
            t0, t1 = t1, t0
        ray_min = max(t0, ray_min)
        ray_max = min(t1, ray_max)
        if ray_max <= ray_min:
            return False
    return True
