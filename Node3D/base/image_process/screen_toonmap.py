import numba
from numba import prange
import numpy as np
from ...constants import cupy


@numba.jit(nopython=True, nogil=True, fastmath=True, parallel=True)
def _screen_toonmap(n, m, data, gamma, multiply):
    for i in prange(n):
        for j in prange(m):
            data[i, j] = max(min(((data[i, j] * multiply) ** gamma) * 255, 255), 0)


@numba.jit(nopython=True, nogil=True, fastmath=True, parallel=True)
def _screen_toonmap3(n, m, data, gamma, multiply):
    for i in prange(n):
        for j in prange(m):
            data[i, j, 0] = max(min(((data[i, j, 0] * multiply) ** gamma) * 255, 255), 0)
            data[i, j, 1] = max(min(((data[i, j, 1] * multiply) ** gamma) * 255, 255), 0)
            data[i, j, 2] = max(min(((data[i, j, 2] * multiply) ** gamma) * 255, 255), 0)


@numba.jit(nopython=True, nogil=True, fastmath=True, parallel=True)
def _screen_toonmap4(n, m, data, gamma, multiply):
    for i in prange(n):
        for j in prange(m):
            data[i, j, 0] = max(min(((data[i, j, 0] * multiply) ** gamma) * 255, 255), 0)
            data[i, j, 1] = max(min(((data[i, j, 1] * multiply) ** gamma) * 255, 255), 0)
            data[i, j, 2] = max(min(((data[i, j, 2] * multiply) ** gamma) * 255, 255), 0)
            data[i, j, 3] = max(min(((data[i, j, 3] * multiply) ** gamma) * 255, 255), 0)


def screen_toonmap_cpu(img, gamma=1.0, multiply=1.0):
    img = img.copy()
    multiply = max(multiply, 0)
    gamma = 1.0 / (2.2 * gamma)
    n = img.shape[0]
    m = img.shape[1]

    if img.shape[-1] == 3:
        _screen_toonmap3(n, m, img, gamma, multiply)
    elif img.shape[-1] == 4:
        _screen_toonmap4(n, m, img, gamma, multiply)
    else:
        if len(img.shape) == 3:
            img = img.reshape((img.shape[0], img.shape[1]))
        _screen_toonmap(n, m, img, gamma, multiply)
    return img.astype(np.uint8)


def screen_toonmap_gpu(img, gamma=1.0, multiply=1.0):
    cu_image = cupy.asarray(img)
    if not np.allclose(multiply, 1.0):
        cu_image *= multiply
    cu_image = cupy.power(cu_image, 1.0 / (2.2 * gamma))
    try:
        cu_image = cupy.clip(cu_image * 255, 0, 255).astype(cupy.uint8)
    except:
        cu_image = (cu_image * 255).astype(cupy.uint8)
    return cupy.asnumpy(cu_image)


def screen_toonmap_cpu_2(img, gamma=1.0, multiply=1.0):
    if np.allclose(multiply, 1.0):
        data = np.power(img, 1.0 / (2.2 * gamma))
    else:
        data = np.power(img * multiply, 1.0 / (2.2 * gamma))
    try:
        data = np.clip(data * 255, 0, 255).astype(np.uint8)
    except:
        data = (data * 255).astype(np.uint8)
    return data


def numpy_default(img):
    s = time()
    a = screen_toonmap_cpu_2(img, 2.2, 2)
    print('numpy_default parallel: ', time() - s)
    return a


def numba_parallel(img):
    s = time()
    a = screen_toonmap_cpu(img, 2.2, 2)
    print('numba parallel: ', time() - s)
    return a


def cuda_parallel(img):
    s = time()
    a = screen_toonmap_gpu(img, 2.2, 2)
    print('numba parallel: ', time() - s)
    return a


if __name__ == "__main__":
    from time import time

    image = np.random.random((1920, 1080))
    # print(image)

    s = numpy_default(image)
    # print(s)

    numba_parallel(image)
    numba_parallel(image)
    a = numba_parallel(image)
    print(np.allclose(a, s))
    # print(a)

    cuda_parallel(image)
    cuda_parallel(image)
    b = cuda_parallel(image)

    print(np.allclose(b, s))
