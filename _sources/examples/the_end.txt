======================
"The End" effect
======================

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/sZMyzzGlsc0&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/sZMyzzGlsc0&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>
        
So let's explain this one: there is a clip with "The End" written in the middle, and *above* this
clip there is the actual movie. The actual movie has a mask which represents
a white (=opaque) circle on a black (=transparent) background. At the begining,
that circle is so large that you see all the actual movie and you don't see
the "The End" clip. Then the circle becomes progressively smaller and as a
consequence you see less of the actual movie and more of the "The End" clip.
    
.. literalinclude:: ../../examples/the_end.py
