MoviePy Docker
===============

Prerequisites
-------------

Docker installed: `Docker Engine for Linux <https://docs.docker.com/engine/install/>`_ or `Docker Desktop for Windows/Mac/Linux <https://docs.docker.com/desktop/>`_.

Build the docker
-----------------
1. Move into the moviepy root dir
2. Build the Dockerfile ::
     
     docker build -t moviepy -f Dockerfile .


How to run the unittests from docker
------------------------------------------------

Run pytest inside the container with the following command ::

     docker run -w /moviepy -it moviepy python -m pytest

Running your own moviepy script from docker
--------------------------------------------

Change directory to where your script is located

If moviepy docker container is already running, you can connect by: ::

     docker exec -it moviepy python myscript.py

If the container isn't running already ::

     docker run -it moviepy bash
     python myscript.py

You can also start a container and run a script in one command: ::

     docker run -it -v `pwd`:/code moviepy python myscript.py
