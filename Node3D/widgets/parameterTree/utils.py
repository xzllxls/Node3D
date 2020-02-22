from scipy.interpolate import interp1d
import numpy as np


def build_curve_ramp(values, pos, kind):
    p = pos.copy()
    p.insert(0,-0.1)
    p.append(1.1)
    values.insert(0,values[0])
    values.append(values[-1])
    try:
        return interp1d(p, values, kind=kind)
    except:
        return None


class color_gradient_builder(object):
    def __init__(self, colors,pos, kind):
        self.rf = None
        self.gf = None
        self.bf = None
        self.build(colors, pos, kind)

    def build(self, colors, pos, kind):
        r = []
        g = []
        b = []
        _pos = []

        for i in range(len(pos)):
            p = pos[i]
            if _pos and p == _pos[-1]:
                continue
            _pos.append(p)
            c = colors[i]
            r.append(c[0])
            g.append(c[1])
            b.append(c[2])
        self.rf = build_curve_ramp(r, _pos, kind)
        self.gf = build_curve_ramp(g, _pos, kind)
        self.bf = build_curve_ramp(b, _pos, kind)

    def getColor(self, pos):
        if self.rf is None or self.gf is None or self.bf is None:
            return None
        r = self.rf(pos)
        g = self.gf(pos)
        b = self.bf(pos)
        return r, g, b

    def getColors(self, keys):
        if self.rf is None or self.gf is None or self.bf is None:
            return None
        n = len(keys)
        r = self.rf(keys).reshape((n,1))
        g = self.gf(keys).reshape((n,1))
        b = self.bf(keys).reshape((n,1))
        return np.hstack([r, g, b])


def get_ramp_colors(colors, pos, kind, keys):
    b = color_gradient_builder(colors, pos, kind)
    return b.getColors(keys)


def get_ramp_color(colors, pos, kind, keys):
    b = color_gradient_builder(colors, pos, kind)
    return b.getColor(keys)