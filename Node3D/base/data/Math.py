import numpy as np


def clamp(value, min, max):
    return np.clip(value, min, max)


def lerp(a, b, fraction):
    fraction = clamp(fraction, 0, 1)
    return a * (1 - fraction) + b * fraction


def fit(value, omin, omax, nmin, nmax):
    v = (value - omin) / (omax - omin)
    return v * (nmax - nmin) + nmin


def fit01(value, min, max):
    return value * (max - min) + min


def fit10(value, min, max):
    return (1.0 - value) * (max - min) + min


def fit11(value, min, max):
    return fit(value, -1, 1, min, max)


def fit_to_01(value, min, max):
    return (value - min) / (max - min)


def fit_11_to_01(value):
    return (value + 1.0) * 0.5
