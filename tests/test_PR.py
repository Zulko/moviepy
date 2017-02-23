"""
Tests meant to be run with pytest
"""

import sys
import os
import pytest

from moviepy.editor import *


def download_youtube_video(url, filename):
    if not os.path.exists(filename):
       print("\nDownloading %s\n" % filename)
       download_webfile(url, filename)
       print("Downloading complete...\n")


def test_PR_339():
    #in caption mode
    overlay = TextClip(txt='foo',
                       color='white',
                       size=(640, 480),
                       method='caption',
                       align='center',
                       fontsize=25)

    #in_label_mode
    overlay = TextClip(txt='foo', method='label')
