# -*- coding: utf-8 -*-
"""Handle retrieving media assets for testing."""
import os

from moviepy.video.io.downloader import download_webfile


def download_url(url, filename):
    """Download a file."""
    if not os.path.exists(filename):
       print('\nDownloading {}\n'.format(filename))
       download_webfile(url, filename)
       print('Downloading complete...\n')

def download_youtube_video(youtube_id, filename):
    """Download a video from youtube."""
    # FYI..  travis-ci doesn't like youtube-dl
    download_url(youtube_id, filename)

def download():
    """Initiate the media asset downloads."""
    if not os.path.exists('media'):
        os.mkdir('media')

    # Define url prefix and path for all media assets.
    github_prefix = 'https://github.com/earney/moviepy_media/raw/master/tests/'
    output = 'media/{}'
    urls = ['/images/python_logo.png', '/images/matplotlib_demo1.png',
            '/images/afterimage.png', '/videos/big_buck_bunny_432_433.webm',
            '/sounds/crunching.mp3', '/images/pigs_in_a_polka.gif',
            '/videos/fire2.mp4', '/videos/big_buck_bunny_0_30.webm',
            '/subtitles/subtitles1.srt', '/misc/traj.txt',
            '/images/vacation_2017.jpg']

    # Loop through download url strings, build out path, and download the asset.
    for url in urls:
        _, tail = os.path.split(url)
        download_url('{}/{}'.format(github_prefix, url), output.format(tail))

    # Download remaining asset.
    download_url('https://data.vision.ee.ethz.ch/cvl/video2gif/kAKZeIzs0Ag.mp4',
                 'media/video_with_failing_audio.mp4')
