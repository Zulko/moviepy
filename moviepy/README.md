Cython Blit
========

Use C-Extensions for Python, a.k.a. Cython, to perform interpolations of two high dimensional matrices rather than directly use NumPy.

Modify "cython_blit.pyx" and setup.py of moviepy will automatically compile it into .c and .so files. It will also be made into a module and can be used by:

    from moviepy.cython_blit import *

Example
--------

    import numpy as np
    from moviepy.cython_blit import cy_update

    im1 = (255 * np.random.random((720, 1280, 3))).astype(np.int16)
    im2 = (255 * np.random.random((720, 1280, 3))).astype(np.int16)
    mask = (np.random.random((720, 1280))).astype(np.float32)

    cy_update(im1, im2, mask)
    # now im2 is updated
