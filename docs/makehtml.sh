make html

# open generated HTML files
if [[ $(uname) == 'Darwin' ]]; then
    open '../../docs/html/index.html' -a Firefox
elif [[ $(uname) == 'Linux' ]]; then
    firefox ../../docs/html/index.html
fi
