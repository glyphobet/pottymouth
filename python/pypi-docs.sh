#!/bin/bash
rm pypi-docs.zip
cp ../readme.html index.html
zip pypi-docs.zip index.html
rm index.html
echo "Now upload pypi-docs.zip to PyPi here: http://pypi.python.org/pypi?%3Aaction=pkg_edit&name=PottyMouth"
echo "Remember to remove pypi-docs.zip when you're done."