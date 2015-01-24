"""
Utilities to get a file from the internet
"""

import os

try: # Py2 and Py3 compatibility
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve

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
        urlretrieve(url, filename)
    else:
        subprocess_call(['youtube-dl', url, '-o', filename])



