#!/bin/sh
make clean html

# open generated HTML files
if [[ $(uname) == 'Darwin' ]]; then
    open 'build/html/index.html' -a Firefox
elif [[ $(uname) == 'Linux' ]]; then
    firefox build/html/index.html
fi
