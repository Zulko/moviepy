.. _refvideofx:

***********************
moviepy.video.fx (vfx)
***********************
The module ``moviepy.video.fx`` regroups functions meant to be used with ``videoclip.fx()``.

For all other modifications, we use ``clip.fx`` and ``clip.fl``. ``clip.fx`` is meant to make it easy to use already-written transformation functions, while  ``clip.fl`` makes it easy to write new transformation functions.

Because this module is starting to get large and will only get larger in the future, it allows two kinds of imports. You can either import a single function like this: ::

    from moviepy.video.fx.scroll import crop
    newclip = myclip.fx( vfx.crop, x1=15)

Or import everything: ::

    import moviepy.video.fx.all as vfx
    newclip = (myclip.fx( vfx.crop, x1=15)
                     .fx( vfx.resize, width=200)
                     .fx( vfx.freeze_at_end, 1))


When you type: ::

    from moviepy.editor import *

the module ``video.fx`` is loaded as ``vfx`` and you can use ``vfx.colorx``, ``vfx.resize`` etc.


.. currentmodule:: moviepy.video.fx.all

.. autosummary::
    :toctree: videofx
    :nosignatures:

    accel_decel
    blackwhite
    blink
    colorx
    crop
    even_size
    fadein
    fadeout
    freeze
    freeze_region
    gamma_corr
    headblur
    invert_colors
    loop
    lum_contrast
    make_loopable
    margin
    mask_and
    mask_color
    mask_or
    mirror_x
    mirror_y
    painting
    resize
    rotate
    scroll
    speedx
    supersample
    time_mirror
    time_symmetrize



