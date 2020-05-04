import numba
import numpy as np
import threading
from ...constants import  cupy


@numba.jit(nopython=True, nogil=True, fastmath=True)
def _pow_thread(data, gamma, start, end):
    for i in range(start, end):
        data[i] = np.power(data[i], gamma)


def gamma_cpu(img, numthreads, gamma):
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


def gamma_gpu(img, gamma):
    gamma = 1.0 / gamma
    img_gpu = cupy.asarray(img)
    return cupy.asnumpy(cupy.power(img_gpu, gamma))
