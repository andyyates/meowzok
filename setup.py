#!/usr/bin/env python3

#this file copied from meld

import glob
import sys
from distutils.core import setup

#import meowzok.build_helpers
import meowzok.conf

if sys.version_info[:2] < meowzok.conf.PYTHON_REQUIREMENT_TUPLE:
    version = ".".join(map(str, meowzok.conf.PYTHON_REQUIREMENT_TUPLE))
    raise Exception("meowzok setup requires Python %s or higher." % version)

setup(
        name=meowzok.conf.__package__,
        version=meowzok.conf.__version__,
        description='Sight reading and Finger dexterity learning environment',
        author='Andrew Yates',
        author_email='andrew.w.yates@gmail.com',
        url='http://schmindie.co.uk',
        license='GPLv2+',
        classifiers=[
            "Development Status :: 3 - Alpha",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
            ],
        keywords=['piano', 'sightreading'],
        packages=[
            'meowzok'
            ],
        package_data={
            'meowzok': ['README', 'COPYING', 'NEWS']
            },
        scripts=['bin/meowzok'],
        data_files=[
            ('share/doc/meowzok-' + meowzok.conf.__version__,
                ['COPYING', 'NEWS']
                ),
            ],
)
