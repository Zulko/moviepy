## Prerequisites
1. Docker installed  [(Docker for Mac, Docker for windows, linux, etc)](https://www.docker.com/get-docker)

## Steps to run the git repo unittests from docker

1.  Build the Dockerfile `` docker build -t moviepy -f Dockerfile . ``
2.  Get a bash prompt in the moviepy container 

```
cd tests
docker run -it -v `pwd`:/tests moviepy bash
```

3. run the tests.. `` python test_issues.py ``

## Running your own moviepy script from docker

Change directory to where your script is located

If already running, you can connect to the running container.

```
docker exec -it moviepy python myscript.py
```

If the container isn't running already

```
docker run -it moviepy/docs bash
python myscript.py
```
