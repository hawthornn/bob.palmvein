.. vim: set fileencoding=utf-8 :
.. author: Pedro Tome <pedro.tome@idiap.ch>
.. date: Thu Mar 15 15:58:57 CEST 2015

.. _installation:

=========================
Installation Instructions
=========================

.. note::
  This documentation includes several ``file://`` links that usually point to files or directories in your source directory.
  When you are reading this documentation online, these links won't work.
  Please read `Generate this documentation`_ on how to create this documentation including working ``file://`` links.

Download
--------

PalmveinRecLib
~~~~~~~~~~~~~~~~
To have a stable version of the PalmveinRecLib, the safest option is to go to the `PalmveinRecLib <http://pypi.python.org/pypi/palmveinreclib>`_ web page on PyPI_ and download the latest version.

Nevertheless, the library is also available as a project of `Idiap at GitHub`_.
To check out the current version of the PalmveinRecLib, go to the console, move to any place you like and call:

.. code-block:: sh

  $ git clone git@github.com:bioidiap/palmveinreclib.git

Be aware that you will get the latest changes and that it might not work as expected.


Bob
~~~

The PalmveinRecLib is a satellite package of Bob_, where most of the image processing, feature extraction, and palmvein recognition algorithms, as well as the evaluation techniques are implemented. This package uses FaceRecLib_ as a parent package.  
In its current version, the PalmveinRecLib requires Bob_ version 2 or greater.
Since version 2.0 there is no need for a global installation of Bob any more, all required packages will be automatically downloaded from PyPi_.

To install `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_, please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

.. note::
  Currently, running Bob_ under MS Windows in not yet supported.
  However, we found that running Bob_ in a virtual Unix environment such as the one provided by VirtualBox_ is a good alternative.

Usually, all possible database satellite packages (called ``bob.db.[...]``) are automatically downloaded from PyPI_.
If you don't want to download the databases, please edit the ``eggs`` section of the buildout.cfg_ configuration file by removing the databases that you don't want.

The ``gridtk`` tool kit is mainly used for submitting submitting jobs to Idiap_'s SGE_ grid.
The latest version also supports to run jobs in parallel on the local machine.
You can safely remove this line from the buildout.cfg_ if you are not at Idiap and if you don't want to launch your experiments in parallel.


Image Databases
~~~~~~~~~~~~~~~

With the PalmveinRecLib you will run palmvein recognition experiments using some default palm vein image databases.
Though the verification protocols are implemented in the PalmveinRecLib, the images are **not included**.
To download the image databases, please refer to the according Web-pages, database URL's will be given in the :ref:`databases` section.


Set-up your PalmveinRecLib
----------------------------

Now, you have everything ready so that you can continue to set up the PalmveinRecLib.
To do this, we use the BuildOut_ system.
To proceed, open a terminal in your FaceRecLib main directory and call:

.. code-block:: sh

  $ python bootstrap-buildout.py
  $ bin/buildout

The first step will generate a `bin <file:../bin>`_ directory in the main directory of the PalmveinRecLib.
The second step automatically downloads all dependencies of the PalmveinRecLib and creates all required scripts that we will need soon.


Test your Installation
~~~~~~~~~~~~~~~~~~~~~~

One of the scripts that were generated during the bootstrap/buildout step is a test script.
To verify your installation, you should run the script by calling:

.. code-block:: sh

  $ bin/nosetests

In case any of the tests fail for unexplainable reasons, please file a bug report through the `GitHub bug reporting system`_.

.. note::
  Usually, all tests should pass with the latest stable versions of the Bob_ packages.
  In other versions, some of the tests may fail.


Generate this documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate this documentation, you call:

.. code-block:: sh

  $ bin/sphinx-build docs sphinx

Afterwards, the documentation is available and you can read it, e.g., by using:

.. code-block:: sh

  $ firefox sphinx/index.html


.. _buildout.cfg: file:../buildout.cfg

.. include:: links.rst

.. _facereclib: http://pythonhosted.org/facereclib/index.html