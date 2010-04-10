#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='PottyMouth',
      py_modules=['PottyMouth'],
      version='1.2.2',
      data_files=[('share/doc/python-pottymouth', ['readme.html',
                                                   'LICENSE.txt',
                                                   'test.py'    ,
                                                   'web.py'     ,
                                                   'profile.py' ,]),],
      # metadata for fun
      author='Matt Chisholm',
      author_email='matt@theory.org',
      description="transform unstructured, untrusted text to safe, valid XHTML",
      license='BSD License',
      keywords='wiki',
      url='http://glyphobet.net/pottymouth',
      download_url='http://glyphobet.net/pottymouth/dist/',
      long_description="""PottyMouth transforms completely unstructured and untrusted text to valid, nice-looking, completely safe XHTML.

PottyMouth is designed to handle input text from non-technical, potentially careless or malicious users. It produces HTML that is completely safe, programmatically and visually, to include on any web page. And you don't need to make your users read any instructions before they start typing. They don't even need to know that PottyMouth is being used.""",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
                   ],
      platforms='All',
      )
