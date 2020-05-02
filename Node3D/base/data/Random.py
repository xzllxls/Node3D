import random
import numpy as np
from math import sin, cos


def rand(seed=None):
    if seed is not None:
        random.seed(seed)
    return random.random()


def rand_int(a, b, seed=None):
    if seed is not None:
        random.seed(seed)
    return random.randint(a, b)


def rand_vector2(seed=None):
    if seed is not None:
        return np.array([rand(seed + 347), rand(seed + 384)])
    return np.random.rand(2)


def rand_vector3(seed=None):
    if seed is not None:
        return np.array([rand(seed + 847), rand(seed + 243), rand(seed + 541)])
    return np.random.rand(3)


def rand_vector4(seed=None):
    if seed is not None:
        return np.array([rand(seed + 347), rand(seed + 24), rand(seed + 354), rand(seed + 78)])
    return np.random.rand(4)


def rand_quaternion(seed=None):
        if seed is None:
            rand = np.random.rand(3)
        else:
            rand = rand_vector3(seed)
        r1 = np.sqrt(1.0 - rand[0])
        r2 = np.sqrt(rand[0])
        pi2 = np.pi * 2.0
        t1 = pi2 * rand[1]
        t2 = pi2 * rand[2]
        return np.array([cos(t2) * r2, sin(t1) * r1, cos(t1) * r1, sin(t2) * r2])


if __name__ == '__main__':
    print(rand_vector3())
