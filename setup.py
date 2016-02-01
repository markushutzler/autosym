#!/usr/bin/env python

from distutils.core import setup

setup(name='autosym',
      version='0.1',
      description='Automatic Schematic Symbol Generation',
      author='Markus Hutzler',
      author_email='markus.hutzler@me.com',
      packages=['autosym', 'autosym.render', ],
      license='GPL3',
      package_dir={'autosym': 'autosym'},
      )