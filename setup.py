#!/usr/bin/env python
''' Installation script for the fos package '''

from os.path import join as pjoin
from glob import glob
from distutils.core import setup
from distutils.extension import Extension
import numpy as np

from build_helpers import make_cython_ext

try:
    import Cython
except ImportError:
    has_cython = False
else:
    has_cython = True
    
col_ext, cmdclass = make_cython_ext(
    'fos.interact.collision',
    has_cython,
    include_dirs = [np.get_include()])


setup(name='fos',
      version='0.3.0.dev',
      description='Free On Shades a visualization library for python',
      author='Fos Devels',
      author_email='garyfallidis@gmail.com',
      url='http://github.com/Garyfallidis/Fos',
      packages=['fos','fos.interact','fos.actor'],
      ext_modules = [col_ext],
      cmdclass    = cmdclass,
      )

