FROM python:3

# Install system dependencies
RUN apt-get -y update && \
    apt-get -y install ffmpeg fonts-liberation locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LC_ALL C.UTF-8

# Upgrade pip
RUN pip install --upgrade pip

# Copy your MoviePy source (assuming you’re developing it)
ADD . /moviepy
WORKDIR /moviepy

# Install MoviePy with extra requirements
RUN pip install -e .

# Install Jupyter
RUN pip install notebook

# Set default working directory for notebooks
WORKDIR /workspace

# Expose Jupyter port
EXPOSE 8888

# Run Jupyter on container start
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
