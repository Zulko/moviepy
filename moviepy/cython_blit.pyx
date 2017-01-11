#cython: boundscheck=False
#cython: wraparound=False

cimport numpy as np

def cy_update(np.ndarray[short, ndim=3] u1, np.ndarray[short, ndim=3] u2, np.ndarray[float, ndim=2] mask):
    cdef unsigned int i, j, k
    for i in xrange(u1.shape[0]):
        for j in xrange(u1.shape[1]):
            for k in xrange(u1.shape[2]):
                u2[i,j,k] = (<short>(mask[i,j] * (u1[i,j,k] - u2[i,j,k]))) + u2[i,j,k]


def cy_update_mask(np.ndarray[float, ndim=2] u1, np.ndarray[float, ndim=2] u2, np.ndarray[float, ndim=2] mask):
    cdef unsigned int i, j, k
    for i in xrange(u1.shape[0]):
        for j in xrange(u1.shape[1]):
            u2[i,j] = mask[i,j] * (u1[i,j] - u2[i,j]) + u2[i,j]
