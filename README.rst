.. vim: set fileencoding=utf-8 :
.. Pedro Tome <pedro.tome@idiap.ch>
.. Thu Jan 15 12:51:09 CEST 2015

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.palmvein/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.palmvein/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.palmvein.svg?branch=master
   :target: https://travis-ci.org/bioidiap/bob.palmvein
.. image:: https://coveralls.io/repos/bioidiap/bob.palmvein/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.palmvein
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.palmvein/tree/master
.. image:: http://img.shields.io/pypi/v/bob.palmvein.png
   :target: https://pypi.python.org/pypi/bob.palmvein
.. image:: http://img.shields.io/pypi/dm/bob.palmvein.png
   :target: https://pypi.python.org/pypi/bob.palmvein


===================================
 The Palmvein Recognition Library
===================================

Welcome to the Palm vein Recognition Library based on Bob.
This library is designed to perform a fair comparison of palm vein recognition algorithms.
It contains scripts to execute various kinds of palm vein recognition experiments on a variety of palm vein image databases, and running the help is as easy as going to the command line and typing::

  $ bin/palmveinverify.py --help


About
-----

This library is developed at the `Biometrics group <http://www.idiap.ch/scientific-research/research-groups/biometric-person-recognition>`_ at the `Idiap Research Institute <http://www.idiap.ch>`_.
The PalmVeinRecLib is designed to run palm vein recognition experiments in a comparable and reproducible manner.

.. note::
  When you are working at Idiap_, you might get a version of the PalmVeinRecLib, where all paths are set up such that you can directly start running experiments.
  Outside Idiap_, you need to set up the paths to point to your databases, please check `Read Further`_ on how to do that.

Databases
.........
To achieve this goal, interfaces to many publicly available facial image databases are contained, and default evaluation protocols are defined, e.g.:

- CASIA Multi-Spectral Palmprint Database [http://biometrics.idealtest.org/dbDetailForUser.do?id=6]
- VERA Palm vein Database [http://www.idiap.ch/scientific-research/resources]

Algorithms
..........
Together with that, a broad variety of traditional and state-of-the-art palm vein recognition algorithms such as:

- Local Binary Pattern Histogram Sequences [ZSG+05]_

is provided.
Furthermore, tools to evaluate the results can easily be used to create scientific plots, and interfaces to run experiments using parallel processes or an SGE grid are provided.

Extensions
..........
On top of these already pre-coded algorithms, the PalmVeinRecLib provides an easy Python interface for implementing new image preprocessors, feature types, palm vein recognition algorithms or database interfaces, which directly integrate into the palmvein recognition experiment.
Hence, after a short period of coding, researchers can compare their new invention directly with already existing algorithms in a fair manner.

References
..........

.. [ZSG+05]  *W. Zhang, S. Shan, W. Gao, X. Chen and H. Zhang*. **Local Gabor binary pattern histogram sequence (LGBPHS): a novel non-statistical model for face representation and recognition**. Computer Vision, IEEE International Conference on, 1:786-791, 2005.

Installation
------------

To download the PalmVeinRecLib, please go to http://pypi.python.org/pypi/palmveinreclib, click on the **download** button and extract the .zip file to a folder of your choice.

The PalmVeinRecLib is a satellite package of the free signal processing and machine learning library Bob_, and some of its algorithms rely on the `CSU Face Recognition Resources`_.
These two dependencies have to be downloaded manually, as explained in the following.

Bob
...

You will need a copy of Bob in version 1.2.0 or newer to run the algorithms.
Please download Bob_ from its webpage.
After downloading, you should go to the console and write::

  $ python bootstrap.py
  $ bin/buildout

This will download all required packages and install them locally.
If you don't want all the database packages to be downloaded, please remove the xbob.db.[database] lines from the ``eggs`` section of the file **buildout.cfg** in the main directory before calling the three commands above.

Test your installation
......................

To verify that your installation worked as expected, you might want to run our test utilities::

  $ bin/nosetests

Usually, all tests should pass, if you use the latest packages of Bob_.
With other versions of Bob_, you might find some failing tests, or some errors might occur.


Cite our paper
--------------

If you use the PalmVeinRecLib in any of your experiments, please cite the following paper::

  @inproceedings{Tome_ICB2015-SpoofingPalmvein,
         author = {Tome, Pedro and Marcel, S{\'{e}}bastien},
       projects = {Idiap, BEAT, TABULA RASA},
          month = may,
          title = {On the Vulnerability of Palm Vein Recognition to Spoofing Attacks},
      booktitle = {The 8th IAPR International Conference on Biometrics (ICB)},
           year = {2015},
            pdf = {http://publications.idiap.ch/downloads/papers/2015/Tome_ICB2015-SpoofingPalmvein.pdf}
}



.. _bob: http://www.idiap.ch/software/bob
.. _idiap: http://www.idiap.ch
.. _bioidiap at github: http://www.github.com/bioidiap


