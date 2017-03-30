FROM ubuntu

# Install numpy using system package manager
RUN apt-get -y update && apt-get -y install python-numpy python-pip

# Add optional but recommended libraries (scipy and friends)
RUN apt-get -y install python-scipy python-sklearn

# MoviePy requires the ffmpeg binary. Ubuntu PPA doesn't work at the
# moment, so install directly from official static binary release.
ADD http://johnvansickle.com/ffmpeg/releases/ffmpeg-2.4-64bit-static.tar.xz /f.tar.xz
RUN cd / && tar xvfJ f.tar.xz
RUN ls -l /ffmpeg*
RUN ln -s /ffmpeg-*/ffmpeg /usr/bin/
RUN ln -s /ffmpeg-*/ffprobe /usr/bin/
# Verify that ffmpeg works.
RUN /usr/bin/ffmpeg || true

ADD . /moviepy
WORKDIR /moviepy
RUN pip install .
