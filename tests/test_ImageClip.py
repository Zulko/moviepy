# -*- coding: utf-8 -*-
"""Image clip tests meant to be run with pytest."""
import sys

import pytest
from moviepy.video.VideoClip import ImageClip

sys.path.append("tests")

import download_media


def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_exifrotate():
    image_file = 'media/balloons_portrait.jpg'
    with ImageClip(image_file, duration=1) as clip:
        assert clip.img.meta['EXIF_MAIN']['ExifImageWidth'] == 4032
        assert clip.img.meta['EXIF_MAIN']['ExifImageHeight'] == 3024
        assert clip.img.meta['EXIF_MAIN']['Orientation'] == 6
        assert clip.size == (3024, 4032)

    with ImageClip(image_file, duration=1, 
                   imageio_params={'exifrotate': False}) as clip:
        assert clip.size == (4032, 3024)


if __name__ == '__main__':
   pytest.main()
