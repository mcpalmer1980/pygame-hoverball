#! /usr/bin/env python2
import sys
import os
try:
    libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
    sys.path.insert(0, libdir)
    print(libdir + ' added to python path')
except:
    # probably running inside py2exe which doesn't set __file__
    print('lib dir not added')

import main

