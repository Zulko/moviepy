"""
Utilities to get a file from the internet
"""

import os

import requests

from moviepy.tools import subprocess_call


def download_webfile(url, filename, overwrite=False):
    """ Small utility to download the file at 'url' under name 'filename'.
    If url is a youtube video ID like z410eauCnH it will download the video
    using youtube-dl (install youtube-dl first !).
    If the filename already exists and overwrite=False, nothing will happen.
    """
    if os.path.exists(filename) and not overwrite:
        return

    if '.' in url:
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

    else:
        try:
            subprocess_call(['youtube-dl', url, '-o', filename])
        except OSError as e:
            raise OSError(
                e.message + '\n A possible reason is that youtube-dl'
                ' is not installed on your computer. Install it with '
                ' "pip install youtube_dl"')
