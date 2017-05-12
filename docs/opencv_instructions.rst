.. _opencv:

So you want to install OpenCV 2.4.6 ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenCV is very optional, its installation is not always simple and I found it to be unstable, be warned !
The installation seems easy for Windows. On linux, here is what I found on the Internet:

- Remove any other version of OpenCV if you installed it through a package manager.
- Unzip the source code of `OpenCV 2.4.6` in some folder. open a terminal in this folder.
- Make a new directory and go into this directory: ::

      mkdir release
      cd release

- Run ``cmake``. Here is the line I used: ::

      cmake -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=OFF -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON ..

- Run ``make``. This may take a few minutes (15 minutes on my computer). ::

      make

- Finally, install. ::

      sudo make install

And voilà !

You can check if it worked by opeing a Python console and typing ::

    import cv2
    print cv2.__version__

Advice: do not throw your ``release`` folder away. If later you have strange bugs with OpenCV involving ``.so`` files, just redo the ``sudo make install`` step.
