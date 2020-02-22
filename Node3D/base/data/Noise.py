import noise
from .Math import fit_11_to_01
from noise import pnoise1, pnoise2, pnoise3
import numpy as np


'''
for i in range(octaves):
    result = amplitude * noise(pos * frequency)
    frequency *= lacunarity
    amplitude *= gain 
    
octaves: level of detail
persistence(gain): steo of amplitude
lacunarity: step of frequency
repeat: frequency
base
'''


def perlin_noise1(x, octaves=1, gain=0.5, lacunarity=2, amp=1, repeat=1024, base=0):
    if type(x) not in [np.ndarray, list]:
        return amp * fit_11_to_01(pnoise1(x, octaves, gain, lacunarity, repeat, base))
    else:
        r = np.empty((len(x),), dtype=np.float64)
        for i, d in enumerate(x):
            r[i] = amp * fit_11_to_01(pnoise1(d, octaves, gain, lacunarity, repeat, base))
        return r


def perlin_noise2(x, y=None, octaves=1, gain=0.5, lacunarity=2, amp=1, repeat=1024, base=0):
    if y is not None:
        return amp * fit_11_to_01(pnoise2(x, y, octaves, gain, lacunarity, repeat, base))
    else:
        r = np.empty((len(x),), dtype=np.float64)
        for i, d in enumerate(x):
            r[i] = amp * fit_11_to_01(pnoise2(d[0], d[1], octaves, gain, lacunarity, repeat, base))
        return r


def perlin_noise3(x, y=None, z=None, octaves=1, gain=0.5, lacunarity=2, amp=1, repeat=1024, base=0):
    if y is not None:
        return amp * fit_11_to_01(pnoise3(x, y, z, octaves, gain, lacunarity, repeat, base))
    else:
        r = np.empty((len(x),), dtype=np.float64)
        for i, d in enumerate(x):
            r[i] = amp * fit_11_to_01(pnoise3(d[0], d[1], d[2], octaves, gain, lacunarity, repeat, base))
        return r


def snoise2(x, y=None, octaves=1, gain=0.5, lacunarity=2, amp=1, repeat=1):
    if y is not None:
        return amp * fit_11_to_01(noise.snoise2(x * repeat, y * repeat, octaves, gain, lacunarity))
    else:
        r = np.empty((len(x),), dtype=np.float64)
        for i, d in enumerate(x):
            r[i] = amp * fit_11_to_01(noise.snoise2(d[0] * repeat, d[1] * repeat, octaves, gain, lacunarity))
        return r


def snoise3(x, y=None, z=None, octaves=1, gain=0.5, lacunarity=2, amp=1, repeat=1):
    if y is not None:
        return amp * fit_11_to_01(noise.snoise3(x * repeat, y * repeat, z * repeat, octaves, gain, lacunarity))
    else:
        r = np.empty((len(x),), dtype=np.float64)
        for i, d in enumerate(x):
            r[i] = amp * fit_11_to_01(noise.snoise3(d[0] * repeat, d[1] * repeat, d[2] * repeat, octaves, gain, lacunarity))
        return r


def snoise4(x, y=None, z=None, w=None, octaves=1, gain=0.5, lacunarity=2, amp=1, repeat=1):
    if y is not None:
        return amp * fit_11_to_01(noise.snoise4(x * repeat, y * repeat, z * repeat, w * repeat, octaves, gain, lacunarity))
    else:
        r = np.empty((len(x),), dtype=np.float64)
        for i, d in enumerate(x):
            r[i] = amp * fit_11_to_01(noise.snoise4(d[0] * repeat, d[1] * repeat, d[2] * repeat, d[3] * repeat, octaves, gain, lacunarity))
        return r


if __name__ == '__main__':
    d = np.random.random((10, 2))
    print(snoise2(d))
