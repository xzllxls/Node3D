import numba
from numba import prange
import numpy as np
import threading
from ...constants import cupy


@numba.jit(nopython=True, nogil=True, fastmath=True)
def _pow_thread(data, gamma, start, end):
    for i in range(start, end):
        data[i] = np.power(data[i], gamma)


def gamma_cpu_thread(img, numthreads, gamma):
    gamma = 1.0 / gamma
    result = img.flatten()
    step = result.size // numthreads
    chunks = []
    for i in range(numthreads):
        if i == (numthreads - 1):
            chunks.append((result, gamma, i * step, result.size))
            continue
        chunks.append((result, gamma, i*step, (i+1) * step))

    threads = [threading.Thread(target=_pow_thread, args=chunk)
               for chunk in chunks]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return result.reshape(img.shape)


@numba.jit(nopython=True, nogil=True, fastmath=True, parallel=True)
def _power_parallel(n, m, data, gamma):
    for i in prange(n):
        for j in prange(m):
            data[i, j] = data[i, j] ** gamma


@numba.jit(nopython=True, nogil=True, fastmath=True, parallel=True)
def _power_parallel3(n, m, data, gamma):
    for i in prange(n):
        for j in prange(m):
            data[i, j, 0] = data[i, j, 0] ** gamma
            data[i, j, 1] = data[i, j, 1] ** gamma
            data[i, j, 2] = data[i, j, 2] ** gamma


@numba.jit(nopython=True, nogil=True, fastmath=True, parallel=True)
def _power_parallel4(n, m, data, gamma):
    for i in prange(n):
        for j in prange(m):
            data[i, j, 0] = data[i, j, 0] ** gamma
            data[i, j, 1] = data[i, j, 1] ** gamma
            data[i, j, 2] = data[i, j, 2] ** gamma
            data[i, j, 3] = data[i, j, 3] ** gamma


def gamma_cpu(data, gamma):
    gamma = 1.0 / gamma
    n = data.shape[0]
    m = data.shape[1]

    dim = 1
    if data.shape[-1] == 3:
        dim = 3
    elif data.shape[-1] == 4:
        dim = 4
    if dim == 1:
        _power_parallel(n, m, data, gamma)
    elif dim == 3:
        _power_parallel3(n, m, data, gamma)
    elif dim == 4:
        _power_parallel4(n, m, data, gamma)


def gamma_gpu(img, gamma):
    gamma = 1.0 / gamma
    img_gpu = cupy.asarray(img)
    return cupy.asnumpy(cupy.power(img_gpu, gamma))
