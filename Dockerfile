FROM python:3

# Install numpy using system package manager
RUN apt-get -y update && apt-get -y install libav-tools imagemagick libopencv-dev python-opencv

# Install some special fonts we use in testing, etc..
RUN apt-get -y install fonts-liberation

RUN apt-get install -y locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LC_ALL C.UTF-8

# do we need all of these, maybe remove some of them?
RUN pip install imageio numpy scipy matplotlib pandas sympy nose decorator tqdm pillow pytest requests

# install scikit-image after the other deps, it doesn't cause errors this way.
RUN pip install scikit-image sklearn

ADD . /var/src/moviepy/
#RUN git clone https://github.com/Zulko/moviepy.git /var/src/moviepy
RUN cd /var/src/moviepy/ && python setup.py install

# install ffmpeg from imageio.
RUN python -c "import imageio; imageio.plugins.ffmpeg.download()"

#add soft link so that ffmpeg can executed (like usual) from command line
RUN ln -s /root/.imageio/ffmpeg/ffmpeg.linux64 /usr/bin/ffmpeg

# modify ImageMagick policy file so that Textclips work correctly.
RUN cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml 
