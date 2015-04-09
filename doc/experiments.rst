.. vim: set fileencoding=utf-8 :
.. author: Pedro Tome <pedro.tome@idiap.ch>
.. date: Thu Jan 15 15:58:57 CEST 2015

.. _experiments:

===================
Running Experiments
===================

For running experiments with a defined setup, you should use the ``bin/palmveinverify.py`` script directly.

In the following sections the available command line arguments are listed.
Sometimes, arguments have a long version starting with ``--`` and a short one starting with a single ``-``.
In this section, only the long names of the arguments are listed, please refer to ``bin/palmveinverify.py --help`` (or short: ``bin/palmveinverify.py -h``) for the abbreviations.

.. _required:

Required Command Line Arguments
-------------------------------
To run a palmvein recognition experiment using the PalmveinRecLib, you have to tell the ``bin/palmveinverify.py`` script, which database, preprocessing, features, and algorithm should be used.
To use this script, you have to specify at least these command line arguments (see also the ``--help`` option):

* ``--database``: The database to run the experiments on, and which protocol to use.
* ``--preprocessing``: The data preprocessing and its parameters.
* ``--features``: The features to extract and their options.
* ``--tool``: The recognition algorithm and all its required parameters.

There is another command line argument that is used to separate the resulting files from different experiments.
Please specify a descriptive name for your experiment to be able to remember, how the experiment was run:

* ``--sub-directory``: A descriptive name for your experiment.


.. _managing-resources:

Managing Resources
~~~~~~~~~~~~~~~~~~
The PalmveinRecLib is designed in a way that makes it very easy to select the setup of your experiments.
Basically, you can specify your algorithm and its configuration in three different ways:

1. You choose one of the registered resources.
   Just call ``bin/resources.py`` or ``bin/palmveinverify.py --help`` to see, which kind of resources are currently registered.
   Of course, you can also register a new resource.
   How this is done is detailed in section :ref:`register-resources`.

   Example:

   .. code-block:: sh

     $ bin/palmveinverify.py --database verapalm

2. You define a configuration file or choose one of the already existing configuration files that are located in `PalmveinRecLib/configurations`_ and its sub-directories.
   How to define a new configuration file, please read section :ref:`configuration-files`.

   Example:

   .. code-block:: sh

     $ bin/palmveinverify.py --preprocessing palmvein-preprocessor

3. You directly put the constructor call of the class into the command line.
   Since the parentheses are special characters in the shell, usually you have to enclose the constructor call into quotes.
   If you, e.g., want to extract MC-MaximumCurvature features, just add a to your command line.

   Example:

   .. code-block:: sh

     $ bin/palmveinverify.py --features lbp-linearbinarypatterns


Of course, you can mix the ways, how you define command line options.

For several databases, preprocessors, feature types, and recognition algorithms the PalmveinRecLib provides configuration files.
They are located in the `PalmveinRecLib/configurations`_ directories.
Each configuration file contains the required information for the part of the experiment, and all required parameters are preset with a suitable default value.
Many of these configuration files with their default parameters are registered as resources, so that you don't need to specify the path.

Since the default values might not be optimized or adapted to your problem, you can modify the parameters according to your needs.
The most simple way is to pass the constructor call directly to the command line (i.e., use option 3).
If you want to remember the parameters, you probably would write another configuration file.
In this case, just copy one of the existing configuration files to a directory of your choice, adapt it, and pass the file location to the ``bin/palmveinverify.py`` script.

In the following, we will provide a detailed explanation of the parameters of the existing :ref:`databases`, :ref:`preprocessors`, :ref:`extractors`, and :ref:`algorithms`.


.. _databases:

Databases
---------
Currently, all implemented databases are taken from Bob_.
To define a common API for all of the databases, the PalmveinRecLib defines the wrapper classes :py:class:`PalmveinRecLib.databases.DatabaseBob` and :py:class:`PalmveinRecLib.databases.DatabaseBobZT` and :py:class:`PalmveinRecLib.databases.DatabaseFileList` for these databases.
The parameters of this wrapper class are:

Required Parameters
~~~~~~~~~~~~~~~~~~~

* ``name``: The name of the database, in lowercase letters without special characters.
  This name will be used as a default sub-directory to separate resulting files of different experiments.
* ``database = bob.db.<DATABASE>(original_directory=...)``: One of the image databases available at `Idiap at GitHub`_.
  Please set the ``original_directory`` and, if required, the ``original_extension`` parameter in the constructor of that database.
* ``protocol``: The name of the protocol that should be used.
  If omitted, the protocol *Default* will be used (which might not be available in all databases, so please specify).

Optional Parameters
~~~~~~~~~~~~~~~~~~~

These parameters can be used to reduce the number of training images.
Usually, there is no need to specify them, but in case your algorithm requires to much memory:

* ``all_files_option``: The options to the database query that will extract all files.
* ``extractor_training_options``: Special options that are passed to the query, e.g., to reduce the number of images in the extractor training.
* ``projector_training_options``: Special options that are passed to the query, e.g., to reduce the number of images in the projector training.
* ``enroller_training_options``: Special options that are passed to the query, e.g., to reduce the number of images in the enroller training.

Implemented Database Interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here we list the database interfaces that are currently available in the PalmveinRecLib.
By clicking on the database name, you open one configuration file of the database, the link in ``<>`` parentheses will link to the ``bob.db`` database package documentation.
If you have an ``image_directory`` different to the one specified in the file, please change the directory accordingly to be able to use the database.

For more information, please also read the `FaceRecLib <http://pythonhosted.org/facereclib/experiments.html#databases>`_ documentation.


.. _preprocessors:

Preprocessors
-------------
Currently, all preprocessors that are defined in PalmveinRecLib perform work on palmvein images and are, hence, used for palmvein recognition.

Palmvein Cropping Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


* ``mask_h``: Height of the cropping palm mask.
* ``mask_w``: Width of the cropping palm mask.  

* ``padding_offset``: An offset to the paddy array to be applied arround the palmvein image.
* ``padding_threshold``: The pixel value of this paddy array.
  Defined to 0.2 to uncontrolled (low quality) palmvein databases and to 0 for controlled (high quality) palmvein databases. (By default 0.2).
      
* ``preprocessing``: The pre-processing applied to the palmvein image before palm contour extraction. 
  By default equal to 'None'.

* ``palmcontour``: The algorithm used to localize the palm contour.
  Options: 'leemaskMatlab' - Implementation based on [LLP09]_, 'leemaskMod' - Modification based on [LLP09]_ for uncontrolled images introduced by author, and 'konomask' - Implementation based on [KUU02]_.

* ``postprocessing``: The post-processing applied to the palmvein image after the palm contour extraction.
  Options:  'None', 'HE' - Histogram Equalization, 'HFE' - High Frequency Enphasis Filtering [ZTXL09]_, 'CircGabor' - Circular Gabor Filters [ZY09]_.


Preprocessor Classes
~~~~~~~~~~~~~~~~~~~~

* :py:class:`PalmveinRecLib.preprocessing.PalmCrop`: Crops the palmvein image to the desired resolution, localize the palm contour and generate the palm mask region to extract features.

.. note::
  Currently, the pre-processing is fixed to 'None' by default.


.. _extractors:

Feature Extractors
------------------
Several different kinds of features can be extracted from the preprocessed data.
Here is the list of classes to perform feature extraction and its parameters.

* :py:class:`PalmveinRecLib.features.lbp`: Extracts Local Binary Patterns features [MD13]_ from the preprocessed data. 
TODO

.. _algorithms:

Recognition Algorithms
----------------------
There are also a variety of recognition algorithms implemented in the PalmveinRecLib.
All palm recognition algorithms are based on the :py:class:`PalmveinRecLib.tools.Tool` base class.
This base class has parameters that some of the algorithms listed below share.
These parameters mainly deal with how to compute a single score when more than one feature is provided for the model or for the probe:

Here is a list of the most important algorithms and their parameters:
TODO



Parallel Execution of Experiments
---------------------------------

By default, all jobs of the palmvein recognition tool chain run sequentially on the local machine.
To speed up the processing, some jobs can be parallelized using the SGE_ grid or using multi-processing on the local machine, using the :ref:`GridTK <gridtk>`.
For this purpose, there is another option:

* ``--grid``: The configuration file for the grid execution of the tool chain.

.. note::
  The current SGE setup is specialized for the SGE_ grid at Idiap_.
  If you have an SGE grid outside Idiap_, please contact your administrator to check if the options are valid.

The SGE_ setup is defined in a way that easily allows to parallelize data preprocessing, feature extraction, feature projection, model enrollment, and scoring jobs.
Additionally, if the training of the extractor, projector, or enroller needs special requirements (like more memory), this can be specified as well.

Several configuration files can be found in the `PalmveinRecLib/configurations/grid <file:../PalmveinRecLib/configurations/grid>`_ directory.
All of them are based on the :py:class:`PalmveinRecLib.utils.GridParameters` class.
Here are the parameters that you can set:

* ``grid``: The type of the grid configuration; currently "sge" and "local" are supported.
* ``number_of_preprocessing_jobs``: Number of parallel preprocessing jobs.
* ``number_of_extraction_jobs``: Number of parallel feature extraction jobs.
* ``number_of_projection_jobs``: Number of parallel feature projection jobs.
* ``number_of_enrollment_jobs``: Number of parallel enrollment jobs (when development and evaluation sets are enabled, both sets will be split separately).
* ``number_of_scoring_jobs``: Number of parallel scoring jobs (when development and evaluation sets are enabled, or ZT-norm is computed, more scoring jobs will be generated).

If the ``grid`` parameter is set to ``'sge'`` (the default), jobs will be submitted to the SGE_ grid.
In this case, the SGE_ queue parameters might be specified, either using one of the pre-defined queues (see `PalmveinRecLib/configurations/grid <file:../PalmveinRecLib/configurations/grid>`_) or using a dictionary of key/value pairs that are sent to the grid during submission of the jobs:

* ``training_queue``: The queue that is used in any of the training (extractor, projector, enroller) steps.
* ``..._queue``: The queue for the ... step.

If the ``grid`` parameter is set to ``local``, all jobs will be run locally.
In this case, the following parameters for the local submission can be modified:

* ``number_of_parallel_processes``: The number of parallel processes that will be run on the local machine.
* ``scheduler_sleep_time``: The interval in which the local scheduler should check for finished jobs and execute new jobs; the sleep time is given in seconds.

and the ``number_of_..._jobs`` are ignored, and ``number_of_parallel_processes`` is used for all of them.

.. note::
  The parallel execution of jobs on the local machine is currently in BETA status and might be unstable.
  If any problems occur, please file a new bug at http://github.com/idiap/gridtk/issues.

When calling the ``bin/palmveinverify.py`` script with the ``--grid ...`` argument, the script will submit all the jobs by taking care of the dependencies between the jobs.
If the jobs are sent to the SGE_ grid (``grid = "sge"``), the script will exit immediately after the job submission.
Otherwise, the jobs will be run locally in parallel and the script will exit after all jobs are finished.

In any of the two cases, the script writes a database file that you can monitor using the ``bin/jman`` command.
Please refer to ``bin/jman --help`` or the :ref:`GridTK documentation <gridtk>` to see the command line arguments of this tool.
The name of the database file by default is **submitted.sql3**, but you can change the name (and its path) using the argument:

* ``--submit-db-file``


Command Line Arguments to change Default Behavior
-------------------------------------------------
Additionally to the required command line arguments discussed above, there are several options to modify the behavior of the PalmveinRecLib experiments.
One set of command line arguments change the directory structure of the output.
By default, the results of the recognition experiment will be written to directory **/idiap/user/<USER>/<DATABASE>/<EXPERIMENT>/<SCOREDIR>/<PROTOCOL>**, while the intermediate (temporary) files are by default written to **/idiap/temp/<USER>/<DATABASE>/<EXPERIMENT>** or **/scratch/<USER>/<DATABASE>/<EXPERIMENT>**, depending on whether the ``--grid`` argument is used or not, respectively:

* <USER>: The Unix username of the person executing the experiments.
* <DATABASE>: The name of the database. It is read from the database configuration.
* <EXPERIMENT>: A user-specified experiment name (see the ``--sub-directory`` argument above).
* <SCOREDIR>: Another user-specified name (``--score-sub-directory`` argument below), e.g., to specify different options of the experiment.
* <PROTOCOL>: The protocol which is read from the database configuration.

These default directories can be overwritten using the following command line arguments, which expects relative or absolute paths:

* ``--temp-directory``
* ``--result-directory`` (for compatibility reasons also ``--user-directory`` can be used)

Re-using Parts of Experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to re-use parts previous experiments, you can specify the directories (which are relative to the ``--temp-directory``, but you can also specify absolute paths):

* ``--preprocessed-data-directory``
* ``--features-directory``
* ``--models-directories`` 

or even trained extractor, projector, or enroller (i.e., the results of the extractor, projector, or enroller training):

* ``--extractor-file``
* ``--enroller-file``

For that purpose, it is also useful to skip parts of the tool chain.
To do that you can use:

* ``--skip-preprocessing``
* ``--skip-extractor-training``
* ``--skip-extraction``
* ``--skip-enroller-training``
* ``--skip-enrollment``
* ``--skip-score-computation``
* ``--skip-concatenation``

although by default files that already exist are not re-created.
To enforce the re-creation of the files, you can use the:

* ``--force``

argument, which of course can be combined with the ``--skip...`` arguments (in which case the skip is preferred).
To run just a sub-selection of the tool chain, you can also use the:

* ``--execute-only``

argument, which takes a list of options out of: ``preprocessing``, ``extractor-training``, ``extraction``, ``projector-training``, ``projection``, ``enroller-training``, ``enrollment``, ``score-computation``, or ``concatenation``.

Sometimes you just want to try different scoring functions.
In this case, you could simply specify a:

* ``--score-sub-directory``

In this case, no feature or model is recomputed (unless you use the ``--force`` option), but only new scores are computed.


Other Arguments
---------------

By default, the algorithms are set up to execute quietly, and only errors are reported.
To change this behavior, you can -- again -- use the

* ``--verbose``

argument several times to increase the verbosity level to show:

1) Warning messages
2) Informative messages
3) Debug messages

When running experiments locally, my personal preference is verbose level 2, which can be enabled by ``--verbose --verbose``, or using the short version of the argument: ``-vv``.

Finally, there is the:

* ``--dry-run``

argument that can be used for debugging purposes or to check that your command line is proper.
When this argument is used, the experiment is not actually executed, but only the steps that would have been executed are printed to console.

.. note::
  Usually it is a good choice to use the ``--dry-run`` option before submitting jobs to the SGE_, just to make sure that all jobs would be submitted correctly and with the correct dependencies.

.. _PalmveinRecLib/configurations: file:../PalmveinRecLib/configurations

.. include:: links.rst
