#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import random

print """This script attempts to crash PottyMouth by "fuzzing" it. 
It creates random strings of symbols for PottyMouth to parse().
If you crash or lock up PottyMouth, email me the input string!"""

from PottyMouth import PottyMouth

parser = PottyMouth(
    url_check_domains=('mysite.com',),
    url_white_lists=(
        'https?://mysite\.com/allowed/service',
        'https?://mysite\.com/safe/url',
    )
)

max_length = 1000
characters = u'abcdefghijklmnopqrstuvwxyz0123456789 \n\r\f\v\t\xa0\u2022>>>:::***-#.)•\'"`/?=&<'
tries = 0

try:
    while True:

        s = ''
        for i in range(random.randint(0, max_length)):
            s += random.choice(characters)

        try:
            start = time.time()
            str(parser.parse(s))
        except KeyboardInterrupt:
            if time.time() - start > 1:
                print "\nAppears to have locked up! Email me this:\n", s
            break
        except:
            print "\nFound bad input! Email me this:\n", s
            break
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
        tries += 1
except KeyboardInterrupt:
    pass
finally:
    print "\nTried", tries, "strings."