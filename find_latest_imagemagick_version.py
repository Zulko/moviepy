import re
from urllib import request

url = "https://legacy.imagemagick.org/script/index.php"

"""This little script parses url above to extract latest image magick version
(major version 6.9), to feed it into CI system. Not the best way for reproducible
builds, but it's preferred for now over storing imagemagick installer into the
git repository
"""

response = request.urlopen(url)
html = response.read().decode(r"utf-8")
r = re.compile(r"6\.9\.[0-9]+-[0-9]+")
version = r.findall(html)
if len(version) == 0:
    raise ValueError(
        "Could not find latest legacy 6.9.X-Y ImageMagick version from {}".format(url)
    )
version = version[0]
# Append Q16 build
version += "-Q16"
print(version)
