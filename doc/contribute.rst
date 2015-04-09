.. vim: set fileencoding=utf-8 :
.. author: Pedro Tome <pedro.tome@idiap.ch>
.. date: Wed Mar 14 11:58:57 CEST 2015

=========================================================================================
Implementing your own Database, Preprocessor, Feature Extractor, or Recognition Algorithm
=========================================================================================

The PalmveinRecLib module is specifically designed to be as flexible as possible while trying to keep things simple.
Therefore, it uses python to implement algorithms.
It is file based so any algorithm can implement its own way of reading and writing data, features or models.
Algorithm configurations are stored in configuration files, so it should be easy to test different parameters of your algorithms without modifying the code.

To implement your own database, preprocessor, feature, or algorithm, simply follow the examples that are already in the PalmveinRecLib.
In the following sections there will be an overview of the functions that need to be implemented.

The PalmveinRecLib is designed in a way that useful default functionalities are executed.
If you want/need to have a different behavior, you can simply add functions to your classes and register these functions, for details please see below.


Implementing your own Functions
-------------------------------

There are two options to add functionality to the PalmveinRecLib.
The preferred option should be to write a satellite package of the PalmveinRecLib, implement everything you want to do, test it and document it.
Please read the :ref:`satellite-packages` section for more details on this.

Here, we describe the second way, which is to add functionality to PalmveinRecLib directly.

Base Classes
~~~~~~~~~~~~
In general, any database, preprocessor, feature extractor or recognition algorithm should be derived from a base class that is detailed below.
This base class provides default implementations of functionality that can be used directly or overwritten in your class.
One of these functions, which is identical to all base classes, is the ``__str__(self)`` function, a special Python construct to convert an object of a class into a string that contains information about the object.
In the PalmveinRecLib, this function is used to write the experimental configuration into a specific text file (by default: **Experiment.info** in the ``--result-directory``).
This information is useful to see the exact configuration of the experiment with which the results was generated.

There are two ways of providing these information for your class:

1. Call the base class constructor and specify all parameters that should be added to the information file.
2. Overwrite the ``__str__(self)`` function in your class, following the example of the base class.

.. _filelist:

Image Databases
~~~~~~~~~~~~~~~
If you have your own database that you want to execute the recognition experiments on, you should first check if you could use the :ref:`Verifcation FileList Database <bob.db.verification.filelist>` interface by defining appropriate file lists for the training set, the model set, and the probes.

For more details, please check the documentation of `FaceRecLib <http://pythonhosted.org/facereclib/contribute.html>`_.


Data Preprocessors
~~~~~~~~~~~~~~~~~~
All preprocessing classes should be derived from the :py:class:`PalmveinRecLib.preprocessing.Preprocessor` class.

If your class returns data that is **not** of type :py:class:`numpy.ndarray`, you might need to overwrite further functions from :py:class:`PalmveinRecLib.preprocessing.Preprocessor` that define the IO of your class:

* ``save_data(data, filename)``: Writes the given data (that has been generated using the ``__call__`` function of this class) to file.
* ``read_data(filename)``: Reads the preprocessed data from file.

By default, the original data is read by :py:func:`bob.io.base.load`.
Hence, data is given as :py:class:`numpy.ndarray`\s.
If you want to use a different IO for the original data (rarely useful...), you might want to overload:

* ``read_original_data(filename)``: Reads the original data from file.

If you plan to use a simple palm cropping for palmvein image processing, you might want to derive your class from the :py:class:`PalmveinRecLib.preprocessing.PalmCrop` class (you don't need to derive from :py:class:`PalmveinRecLib.preprocessing.Preprocessor ` in this case).
In this case, just add a ``**kwargs`` parameter to your constructor, call the palmvein crop constructor with these parameters: ``PalmveinRecLib.preprocessing.PalmCrop.__init__(self, **kwargs)``, and call the ``self.palm_crop(image)`` in your ``__call__`` function.
For an example of this behavior, you might have a look into the `PalmveinRecLib.preprocessing.palm_crop_None_HE <file:../PalmveinRecLib/preprocessing/palm_crop_None_HE.py>`_ class.


Feature Extractors
~~~~~~~~~~~~~~~~~~
Feature extractors should be derived from the :py:class:`PalmveinRecLib.features.Extractor` class.
Your extractor class has to provide at least the functions:

* ``__init__(self, <parameters>)``: Initializes the feature extraction algorithm with the parameters it needs.
  Please call the base class constructor in this constructor, e.g. as ``PalmveinRecLib.features.Extractor.__init__(self, ...)`` (there are more parameters to this constructor, see below).
* ``__call__(self, data) -> feature``: Extracts the feature from the given preprocessed data.
  By default, the returned feature should be a :py:class:`numpy.ndarray`.

If your features are not of type :py:class:`numpy.ndarray`, please overwrite the ``save_feature`` function to write features of other types.
Please also overwrite the function to read your kind of features:

* ``save_feature(self, feature, feature_file)``: Saves the feature (as returned by the ``__call__`` function) to the given file name.
* ``read_feature(self, feature_file) -> feature``: Reads the feature (as written by the ``save_feature`` function) from the given file name.

.. note::
  If your feature is of a class that contains and is written via a ``save(bob.io.base.HDF5File)`` method, you do not need to define a ``save_feature`` function.
  However, the ``read_feature`` function is required in this case.

If the feature extraction process requires to read a trained extractor model from file, simply overload the function:

* ``load(self, extractor_file)``: Loads the extractor from file.
  This function is called at least once before the ``__call__`` function is executed.


Recognition Algorithms
~~~~~~~~~~~~~~~~~~~~~~
Implementing your recognition algorithm should be as straightforward.
Simply derive your class from the :py:class:`PalmveinRecLib.tools.Tool` class.

  .. note::
    When you use a distance measure in your scoring function, and lower distances represents higher probabilities of having the same identity, please return the negative distance.

And once more, if the projected feature is not of type ``numpy.ndarray``, overwrite the methods:

* ``save_feature(feature, feature_file)``: Writes the feature (as returned by the ``project`` function) to file.
* ``read_feature(feature_file) -> feature``: Reads and returns the feature (as written by the ``write_feature`` function).

By default, it is assumed that both the models and the probe features are of type :py:class:`numpy.ndarray`.
If your ``score`` function expects models and probe features to be of a different type, you should overwrite the functions:

* ``save_model(self, model, model_file)``: writes the model (as returned by the ``enroll`` function)
* ``read_model(self, model_file) -> model``: reads the model (as written by the ``write_model`` function) from file.
* ``read_probe(self, probe_file) -> feature``: reads the probe feature from file.

  .. note::
    In many cases, the ``read_feature`` and ``read_probe`` functions are identical (if both are present).

Finally, the :py:class:`PalmveinRecLib.tools.Tool` class provides default implementations for the case that models store several features, or that several probe features should be combined into one score.


Executing experiments with your classes
---------------------------------------
Finally, executing experiments using your database, preprocessor, feature extraction, and/or recognition tool should be as easy as using the tools that are already available.
Nonetheless, it might be a good idea to first run the experiments locally (i.e., calling the ``bin/palmveinverify.py -vvv`` without the ``--grid`` option) to see if your functions do work and do provide expected results.


Adding Unit Tests
-----------------
To make sure that your piece of code it working properly, you should add a test case for your class.
The PalmveinRecLib, as well as Bob_, rely on `nose tests <http://pypi.python.org/pypi/nose>`_ to run the unit tests.
To implement a unit test for your contribution, you simply can create a python file with a name containing 'test' in your package.
In the PalmveinRecLib, these files are located in `PalmveinRecLib/tests <file:../PalmveinRecLib/tests>`_.

In the test file, please write a test class that derives from ``unittest.TestCase``.
Any function name containing the string ``test`` will be automatically found and executed when running ``bin/nosetests``.
In your test function, please assure that all aspects of your contribution are thoroughly tested and that all test cases pass.
Also remember that your tests need to run on different machines with various operating systems, so don't test floating point values for equality.


.. _configuration-files:

Adding Configuration Files
--------------------------
After your code is tested, you should provide a configuration file for your algorithm.
A configuration file basically consists of a constructor call to your new class with a useful (yet not necessarily optimized) set of parameters.
Depending on your type of contribution, you should write a line like:

* ``database = PalmveinRecLib.databases.<YourDatabase>(<YourParameters>)``
* ``preprocessor = PalmveinRecLib.preprocessing.<YourPreprocessor>(<YourParameters>)``
* ``feature_extractor = PalmveinRecLib.features.<YourExtractor>(<YourParameters>)``
* ``tool = PalmveinRecLib.tools.<YourAlgorithm>(<YourParameters>)``

and save the configuration file into the according sub-directory of `PalmveinRecLib/configurations <file:../PalmveinRecLib/configurations>`_.


.. _register-resources:

Registering your Code as a Resource
-----------------------------------
Now, you should be able to register this configuration file as a resource, so that you can use the configuration from above by a simple ``<shortcut>`` of your choice.
Please open the `setup.py <file:../setup.py>`_ file in the base directory of your satellite package and edit the ``entry_points`` section.
Depending on your type of algorithm, you have to add:

* ``'PalmveinRecLib.database': [ '<your-database-shortcut> = <your-database-configuration>.database' ]``
* ``'PalmveinRecLib.preprocessor': [ '<your-preprocessor-shortcut> = <your-preprocessor-configuration>.preprocessor' ]``
* ``'PalmveinRecLib.feature_extractor': [ '<your-extractor-shortcut> = <your-extractor-configuration>.feature_extractor' ]``
* ``'PalmveinRecLib.tool': [ '<your-recognition-algorithm-shortcut> = <your-algorithm-configuration>.tool' ]``

After re-running ``bin/buildout``, your new resource should be listed in the output of ``bin/resources.py``.


.. include:: links.rst
