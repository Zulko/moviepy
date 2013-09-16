======================================
Placing clips according to a picture
======================================


So how do you do some complex compositing like this ?

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/1hdgNxX-tas&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/1hdgNxX-tas&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

It takes a lot of bad taste, and a segmenting tool

In this script we will use this image (generated with Inkscape):

.. figure:: compo_from_image.jpeg

We will find the regions of this image and fit the different clips into these regions:

.. literalinclude:: ../../examples/compo_from_image.py


(note that some pictures are distorted here as their size has been modified without care for their aspect ratio. This could be changed with a few more lines.)


