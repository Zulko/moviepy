"""Obtain the latest ImageMagick version from official repositories."""

import sys
from urllib.request import urlopen


BINARIES_URL = "https://imagemagick.org/archive/binaries/"

content = urlopen(BINARIES_URL).read().decode("utf-8")

for line in reversed(content.split("<td>")):
    if 'static.exe">ImageMagick' in line:
        filename = line.split('"')[1]
        sys.stdout.write(f"{BINARIES_URL}{filename}\n")
        break
