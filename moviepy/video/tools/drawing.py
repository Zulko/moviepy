"""Deals with making images (np arrays). It provides drawing
methods that are difficult to do with the existing Python libraries.
"""

import numpy as np


def blit(im1, im2, pos=None, mask=None):
    """Blit an image over another.
    Blits ``im1`` on ``im2`` as position ``pos=(x,y)``, using the
    ``mask`` if provided.
    """
    if pos is None:
        pos = (0, 0)
    else:
        # Cast to tuple in case pos is not subscriptable.
        pos = tuple(pos)
    im2.paste(im1, pos, mask)
    return im2


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

    size
        Size (width, height) in pixels of the final picture/array.

    p1, p2
        Coordinates (x,y) in pixels of the limit point for ``color_1``
        and ``color_2``. The color 'before' ``p1`` is ``color_1`` and it
        gradually changes in the direction of ``p2`` until it is ``color_2``
        when it reaches ``p2``.

    vector
        A vector [x,y] in pixels that can be provided instead of ``p2``.
        ``p2`` is then defined as (p1 + vector).

    color_1, color_2
        Either floats between 0 and 1 (for gradients used in masks)
        or [R,G,B] arrays (for colored gradients).

    shape
        'linear', 'bilinear', or 'circular'.
        In a linear gradient the color varies in one direction,
        from point ``p1`` to point ``p2``.
        In a bilinear gradient it also varies symetrically from ``p1``
        in the other direction.
        In a circular gradient it goes from ``color_1`` to ``color_2`` in all
        directions.

    offset
        Real number between 0 and 1 indicating the fraction of the vector
        at which the gradient actually starts. For instance if ``offset``
        is 0.9 in a gradient going from p1 to p2, then the gradient will
        only occur near p2 (before that everything is of color ``color_1``)
        If the offset is 0.9 in a radial gradient, the gradient will
        occur in the region located between 90% and 100% of the radius,
        this creates a blurry disc of radius d(p1,p2).

    Returns
    -------

    image
        An Numpy array of dimensions (W,H,ncolors) of type float
        representing the image of the gradient.


    Examples
    --------

    >>> grad = color_gradient(blabla).astype('uint8')

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
            for v in [vector, -vector]
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
        n_vec = vector / norm ** 2  # norm 1/norm(vector)

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
    """Make an image splitted in 2 colored regions.

    Returns an array of size ``size`` divided in two regions called 1 and
    2 in what follows, and which will have colors color_1 and color_2
    respectively.

    Parameters
    ----------

    x: (int)
        If provided, the image is splitted horizontally in x, the left
        region being region 1.

    y: (int)
        If provided, the image is splitted vertically in y, the top region
        being region 1.

    p1, p2:
        Positions (x1,y1),(x2,y2) in pixels, where the numbers can be
        floats. Region 1 is defined as the whole region on the left when
        going from ``p1`` to ``p2``.

    p1, vector:
        ``p1`` is (x1,y1) and vector (v1,v2), where the numbers can be
        floats. Region 1 is then the region on the left when starting
        in position ``p1`` and going in the direction given by ``vector``.

    gradient_width
        If not zero, the split is not sharp, but gradual over a region of
        width ``gradient_width`` (in pixels). This is preferable in many
        situations (for instance for antialiasing).


    Examples
    --------

    >>> size = [200,200]
    >>> # an image with all pixels with x<50 =0, the others =1
    >>> color_split(size, x=50, color_1=0, color_2=1)
    >>> # an image with all pixels with y<50 red, the others green
    >>> color_split(size, x=50, color_1=[255,0,0], color_2=[0,255,0])
    >>> # An image splitted along an arbitrary line (see below)
    >>> color_split(size, p1=[20,50], p2=[25,70] color_1=0, color_2=1)
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

    # if we are here, it means we didn't exit with a proper 'return'
    print("Arguments in color_split not understood !")
    raise


def circle(screensize, center, radius, color=1.0, bg_color=0, blur=1):
    """Draw an image with a circle.

    Draws a circle of color ``color``, on a background of color ``bg_color``,
    on a screen of size ``screensize`` at the position ``center=(x,y)``,
    with a radius ``radius`` but slightly blurred on the border by ``blur``
    pixels
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
