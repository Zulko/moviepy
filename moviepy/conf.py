"""
Configuration MoviePy


This file enables you to specify a configuration for MoviePy. In
particular you can enter the path to the FFMPEG and ImageMagick
binaries.

Instructions
--------------


FFMPEG_BINARY
    Normally you can leave this one to its default (None) and MoviePy
    will detect automatically the right name, which will be either
    'ffmpeg' (on linux) or 'ffmpeg.exe' (on windows). If you want to
    use a binary at a special location on you disk, enter it like that:

    FFMPEG_BINARY = r"path/to/ffmpeg(.exe)"
    
    Warning: the 'r' before the path is important, especially on Windows.

    
IMAGEMAGICK_BINARY
    For linux users, 'convert' should be fine.
    For Windows users, you must specify the path to the ImageMagick
    'convert' binary. For instance:

    IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-6.8.8-Q16\convert.exe" 

You can run this file to check that FFMPEG has been detected.
"""

# =====================================================================
# CODE. Don't write anything below this line !

import os
import subprocess as sp
import xml.etree.ElementTree as ET
from xml.dom import minidom 
from xml.etree.ElementTree import Element, SubElement

def getConfFilePath():
    currntPath = os.path.split(__file__)
    confFilePath = os.path.join(os.path.split(__file__)[0], 'moviepy.conf')
    if os.path.isfile(confFilePath):
        return confFilePath
    else:
        raise Exception("Configuration File doesn't Exists.")

def try_cmd(cmd):    
        try:
            proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            proc.communicate()
        except:
            return False
        else:
            return True

tree = ET.parse(getConfFilePath())
elem = tree.getroot()

FFMPEG_BINARY = elem[0].attrib['value']
IMAGEMAGICK_BINARY = elem[1].attrib['value']

if FFMPEG_BINARY is None:
    if try_cmd(['ffmpeg']):
        FFMPEG_BINARY = 'ffmpeg'
    elif try_cmd(['ffmpeg.exe']):
        FFMPEG_BINARY = 'ffmpeg.exe'
    else:
        raise IOError("FFMPEG binary not found. Try installing MoviePy"
                      " manually and specify the path to the binary in"
                      " the file conf.py")

if __name__ == "__main__":
    if try_cmd([FFMPEG_BINARY]):
        print( "MoviePy : ffmpeg successfully found." )
    else:
        print( "MoviePy : can't find ffmpeg." )
        
        
