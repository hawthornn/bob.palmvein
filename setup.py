#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pedro Tome <pedro.tome@idiap.ch>
# Tue 25 Mar 18:18:08 2014 CEST
#
# Copyright (C) 2015 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring adminstrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name='bob.palmvein',
    version=version,
    description='Palmvein recognition based on Bob and the facereclib',

    url='https://github.com/bioidiap/bob.palmvein',
    license='LICENSE.txt',
    author='Pedro Tome',
    author_email='pedro.tome@idiap.ch',
    keywords="Palmvein recognition, palmvein verification, reproducible research, facereclib",

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe = False,

    
    install_requires=[
      'setuptools',
      'bob.io.base',
      'bob.core',
      'bob.ip.base',
      'bob.ip.color',
      'bob.sp',
      'bob.io.matlab',
      'facereclib'
            
    ],

    namespace_packages = [
      'bob',
    ],
    
    entry_points={

      # scripts should be declared using this entry:
      'console_scripts': [
        'palmveinverify.py = bob.palmvein.script.palmveinverify:main',
        'scores2spoofingfile.py = bob.palmvein.script.scores2spoofingfile:main',
        'scoresanalysis.py = bob.palmvein.script.scoresanalysis:main',
        'evaluatesys.py = bob.palmvein.script.evaluatesys:main',
        ],
      
      # registered database short cuts
      'facereclib.database': [
        #'casiapalm             = bob.palmvein.configurations.databases.casiapalm:database',
        'verapalm              = bob.palmvein.configurations.databases.verapalm:database',
        #'verapalmraw              = bob.palmvein.configurations.databases.verapalmraw:database',
        #'verapalmroi           = bob.palmvein.configurations.databases.verapalmroi:database',
        #'verapalmTS            = bob.palmvein.configurations.databases.verapalmTS:database',
        #'verapalmroiTS         = bob.palmvein.configurations.databases.verapalmroiTS:database',
      ],

      # registered preprocessings
      'facereclib.preprocessor': [
        'palmvein-preprocessor = bob.palmvein.configurations.preprocessing.palm_crop:preprocessor',
               
      ],


      # registered feature extractors
      'facereclib.feature_extractor': [
        'lbp-localbinarypatterns   = bob.palmvein.configurations.features.lbp:feature_extractor',
        
      ],

      # registered palmvein recognition algorithms
      'facereclib.tool': [
        'match-lbp      = facereclib.configurations.tools.lgbphs:tool',
       ], 

      # registered SGE grid configuration files
      'facereclib.grid': [
        'gpu               = bob.palmvein.configurations.grid.gpu:grid',
        'gpu2              = bob.palmvein.configurations.grid.gpu2:grid',
        'gpu3              = bob.palmvein.configurations.grid.gpu3:grid',
        'grid              = bob.palmvein.configurations.grid.grid:grid',
        'demanding         = bob.palmvein.configurations.grid.demanding:grid',
        'very-demanding    = bob.palmvein.configurations.grid.very_demanding:grid',
        'gbu               = bob.palmvein.configurations.grid.gbu:grid',
        'small             = bob.palmvein.configurations.grid.small:grid',        
      ],

      # tests that are _exported_ (that can be executed by other packages) can
      # be signalized like this:
      'bob.test': [
        'tests = bob.palmvein.tests.test:PalmveinTests',
                
      ],

      },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
