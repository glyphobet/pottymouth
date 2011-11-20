#!/bin/sh
set -e

# update Debian changelog
DEBEMAIL='matt@theory.org' dch -v `python -c 'import pottymouth; print pottymouth.__version__'`-0

# remove old deb files
rm ../python-pottymouth_* -f

# build package
debuild -uc -us
