========================================
Tracking and blurring someone's face
========================================

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/FWCKYTRCrBI&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/FWCKYTRCrBI&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

First we will need to track the face, i.e. to get two functions ``fx`` and ``fy`` such that ``(fx(t),fy(t))`` gives the position of the center of the head at time ``t``. This will be easily done with
`manual_tracking`. Then we will need to blur the area of the video around the center of the head.

.. literalinclude:: ../../examples/headblur.py
