#!/bin/bash

# Upload to PyPi: (There are bugs in Python < 2.7 that prevent this from working)
/opt/local/bin/python2.7 setup.py bdist_egg register upload
/opt/local/bin/python2.7 setup.py sdist register upload