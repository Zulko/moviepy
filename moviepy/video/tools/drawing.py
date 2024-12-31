"""Deals with making images (np arrays). It provides drawing
methods that are difficult to do with the existing Python libraries.
"""

import numpy as np


def color_gradient(
    size,
    p1,
    p2=None,
    vector=None,
    radius=None,
    color_1=0.0,
    color_2=1.0,
    shape="linear",
    offset=0,
):
    """Draw a linear, bilinear, or radial gradient.

    The result is a picture of size ``size``, whose color varies
    gradually from color `color_1` in position ``p1`` to color ``color_2``
    in position ``p2``.

    If it is a RGB picture the result must be transformed into
    a 'uint8' array to be displayed normally:

    Parameters
    ----------

    size : tuple or list
        Size (width, height) in pixels of the final image array.

    p1 : tuple or list
       Position for the first coordinate of the gradient in pixels (x, y).
       The color 'before' ``p1`` is ``color_1`` and it gradually changes in
       the direction of ``p2`` until it is ``color_2`` when it reaches ``p2``.

    p2 : tuple or list, optional
       Position for the second coordinate of the gradient in pixels (x, y).
        Coordinates (x, y)  of the limit point for ``color_1``
        and ``color_2``.

    vector : tuple or list, optional
        A vector (x, y) in pixels that can be provided instead of ``p2``.
        ``p2`` is then defined as (p1 + vector).

    color_1 : tuple or list, optional
        Starting color for the gradient. As default, black. Either floats
        between 0 and 1 (for gradients used in masks) or [R, G, B] arrays
        (for colored gradients).

    color_2 : tuple or list, optional
        Color for the second point in the gradient. As default, white. Either
        floats between 0 and 1 (for gradients used in masks) or [R, G, B]
        arrays (for colored gradients).

    shape : str, optional
        Shape of the gradient. Can be either ``"linear"``, ``"bilinear"`` or
        ``"circular"``. In a linear gradient the color varies in one direction,
        from point ``p1`` to point ``p2``. In a bilinear gradient it also
        varies symmetrically from ``p1`` in the other direction. In a circular
        gradient it goes from ``color_1`` to ``color_2`` in all directions.

    radius : float, optional
        If ``shape="radial"``, the radius of the gradient is defined with the
        parameter ``radius``, in pixels.

    offset : float, optional
        Real number between 0 and 1 indicating the fraction of the vector
        at which the gradient actually starts. For instance if ``offset``
        is 0.9 in a gradient going from p1 to p2, then the gradient will
        only occur near p2 (before that everything is of color ``color_1``)
        If the offset is 0.9 in a radial gradient, the gradient will
        occur in the region located between 90% and 100% of the radius,
        this creates a blurry disc of radius ``d(p1, p2)``.

    Returns
    -------

    image
        An Numpy array of dimensions (width, height, n_colors) of type float
        representing the image of the gradient.

    Examples
    --------

    .. code:: python

        color_gradient((10, 1), (0, 0), p2=(10, 0))  # from white to black
        #[[1.  0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1]]
        # from red to green
        color_gradient(
            (10, 1), (0, 0),
            p2=(10, 0),
            color_1=(255, 0, 0),
            color_2=(0, 255, 0)
        )
        # [[[  0.  255.    0. ]
        #   [ 25.5 229.5   0. ]
        #   [ 51.  204.    0. ]
        #   [ 76.5 178.5   0. ]
        #   [102.  153.    0. ]
        #   [127.5 127.5   0. ]
        #   [153.  102.    0. ]
        #   [178.5  76.5   0. ]
        #   [204.   51.    0. ]
        #   [229.5  25.5   0. ]]]
    """
    # np-arrayize and change x,y coordinates to y,x
    w, h = size

    color_1 = np.array(color_1).astype(float)
    color_2 = np.array(color_2).astype(float)

    if shape == "bilinear":
        if vector is None:
            if p2 is None:
                raise ValueError("You must provide either 'p2' or 'vector'")
            vector = np.array(p2) - np.array(p1)

        m1, m2 = [
            color_gradient(
                size,
                p1,
                vector=v,
                color_1=1.0,
                color_2=0.0,
                shape="linear",
                offset=offset,
            )
            for v in [vector, [-v for v in vector]]
        ]

        arr = np.maximum(m1, m2)
        if color_1.size > 1:
            arr = np.dstack(3 * [arr])
        return arr * color_1 + (1 - arr) * color_2

    p1 = np.array(p1[::-1]).astype(float)

    M = np.dstack(np.meshgrid(range(w), range(h))[::-1]).astype(float)

    if shape == "linear":
        if vector is None:
            if p2 is not None:
                vector = np.array(p2[::-1]) - p1
            else:
                raise ValueError("You must provide either 'p2' or 'vector'")
        else:
            vector = np.array(vector[::-1])

        norm = np.linalg.norm(vector)
        n_vec = vector / norm**2  # norm 1/norm(vector)

        p1 = p1 + offset * vector
        arr = (M - p1).dot(n_vec) / (1 - offset)
        arr = np.minimum(1, np.maximum(0, arr))
        if color_1.size > 1:
            arr = np.dstack(3 * [arr])
        return arr * color_1 + (1 - arr) * color_2

    elif shape == "radial":
        if (radius or 0) == 0:
            arr = np.ones((h, w))
        else:
            arr = (np.sqrt(((M - p1) ** 2).sum(axis=2))) - offset * radius
            arr = arr / ((1 - offset) * radius)
            arr = np.minimum(1.0, np.maximum(0, arr))

        if color_1.size > 1:
            arr = np.dstack(3 * [arr])
        return (1 - arr) * color_1 + arr * color_2
    raise ValueError("Invalid shape, should be either 'radial', 'linear' or 'bilinear'")


def color_split(
    size,
    x=None,
    y=None,
    p1=None,
    p2=None,
    vector=None,
    color_1=0,
    color_2=1.0,
    gradient_width=0,
):
    """Make an image split in 2 colored regions.

    Returns an array of size ``size`` divided in two regions called 1 and
    2 in what follows, and which will have colors color_1 and color_2
    respectively.

    Parameters
    ----------

    x : int, optional
        If provided, the image is split horizontally in x, the left
        region being region 1.

    y : int, optional
        If provided, the image is split vertically in y, the top region
        being region 1.

    p1, p2: tuple or list, optional
        Positions (x1, y1), (x2, y2) in pixels, where the numbers can be
        floats. Region 1 is defined as the whole region on the left when
        going from ``p1`` to ``p2``.

    p1, vector: tuple or list, optional
        ``p1`` is (x1,y1) and vector (v1,v2), where the numbers can be
        floats. Region 1 is then the region on the left when starting
        in position ``p1`` and going in the direction given by ``vector``.

    gradient_width : float, optional
        If not zero, the split is not sharp, but gradual over a region of
        width ``gradient_width`` (in pixels). This is preferable in many
        situations (for instance for antialiasing).

    Examples
    --------

    .. code:: python

        size = [200, 200]

        # an image with all pixels with x<50 =0, the others =1
        color_split(size, x=50, color_1=0, color_2=1)

        # an image with all pixels with y<50 red, the others green
        color_split(size, x=50, color_1=[255, 0, 0], color_2=[0, 255, 0])

        # An image split along an arbitrary line (see below)
        color_split(size, p1=[20, 50], p2=[25, 70], color_1=0, color_2=1)
    """
    if gradient_width or ((x is None) and (y is None)):
        if p2 is not None:
            vector = np.array(p2) - np.array(p1)
        elif x is not None:
            vector = np.array([0, -1.0])
            p1 = np.array([x, 0])
        elif y is not None:
            vector = np.array([1.0, 0.0])
            p1 = np.array([0, y])

        x, y = vector
        vector = np.array([y, -x]).astype("float")
        norm = np.linalg.norm(vector)
        vector = max(0.1, gradient_width) * vector / norm
        return color_gradient(
            size, p1, vector=vector, color_1=color_1, color_2=color_2, shape="linear"
        )
    else:
        w, h = size
        shape = (h, w) if np.isscalar(color_1) else (h, w, len(color_1))
        arr = np.zeros(shape)
        if x:
            arr[:, :x] = color_1
            arr[:, x:] = color_2
        elif y:
            arr[:y] = color_1
            arr[y:] = color_2
        return arr


def circle(screensize, center, radius, color=1.0, bg_color=0, blur=1):
    """Draw an image with a circle.

    Draws a circle of color ``color``, on a background of color ``bg_color``,
    on a screen of size ``screensize`` at the position ``center=(x, y)``,
    with a radius ``radius`` but slightly blurred on the border by ``blur``
    pixels.

    Parameters
    ----------

    screensize : tuple or list
        Size of the canvas.

    center : tuple or list
        Center of the circle.

    radius : float
        Radius of the circle, in pixels.

    bg_color : tuple or float, optional
        Color for the background of the canvas. As default, black.

    blur : float, optional
        Blur for the border of the circle.

    Examples
    --------

    .. code:: python

        from moviepy.video.tools.drawing import circle

        circle(
            (5, 5),  # size
            (2, 2),  # center
            2,      # radius
        )
        # array([[0.        , 0.        , 0.        , 0.        , 0.        ],
        #        [0.        , 0.58578644, 1.        , 0.58578644, 0.        ],
        #        [0.        , 1.        , 1.        , 1.        , 0.        ],
        #        [0.        , 0.58578644, 1.        , 0.58578644, 0.        ],
        #        [0.        , 0.        , 0.        , 0.        , 0.        ]])
    """
    offset = 1.0 * (radius - blur) / radius if radius else 0
    return color_gradient(
        screensize,
        p1=center,
        radius=radius,
        color_1=color,
        color_2=bg_color,
        shape="radial",
        offset=offset,
    )
