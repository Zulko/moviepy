"""Utilities to get a file from the internet."""

import os
import shutil
import urllib.request

from moviepy.tools import subprocess_call


def download_webfile(url, filename, overwrite=False):
    """Small utility to download the file at ``url`` under name ``filename``.

    Parameters
    ----------

    url : str
      If url is a youtube video ID like z410eauCnH it will download the video
      using youtube-dl. Requires youtube-dl (pip install youtube-dl).

    filename : str
      Path to the new downloaded file location.

    overwrite : bool, optional
      If the filename already exists and overwrite=False, nothing will happen.
      Use it to force destination file overwriting.

    Examples
    --------

    >>> from moviepy.io.downloader import download_website
    >>>
    >>> download_website(
    ...     "http://localhost:8000/media/chaplin.mp4",
    ...     "media/chaplin-copy.mp4",
    ... )
    >>>
    """
    if os.path.exists(filename) and not overwrite:  # pragma: no cover
        return

    if "." in url:
        with urllib.request.urlopen(url) as req, open(filename, "wb") as f:
            shutil.copyfileobj(req, f, 128)

    else:
        try:
            subprocess_call(["youtube-dl", url, "-o", filename])
        except OSError as e:
            raise OSError(
                (
                    "Error running youtube-dl.\n%sA possible reason is that"
                    " youtube-dl is not installed on your computer. Install it "
                    " with 'pip install youtube_dl'."
                )
                % ((e.message + "\n" if hasattr(e, "message") else ""))
            )
