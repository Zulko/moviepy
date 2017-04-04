Moviepy Docker
===============

Prequisites
-------------

1. Docker installed `Docker for Mac, Docker for windows, linux, etc <https://www.docker.com/get-docker/>`_
2. Build the Dockerfile ::
     
     docker build -t moviepy -f Dockerfile .


Steps to run the git repo unittests from docker
------------------------------------------------

Get a bash prompt in the moviepy container ::

     cd tests
     docker run -it -v `pwd`:/tests moviepy bash

Run the tests ::
  
     cd tests
     python test_issues.py

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
