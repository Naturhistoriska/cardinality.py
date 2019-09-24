cardinality.py
==============

``cardinality.py`` is a small tool written in Python for examining
the cardinality of a relation between two datasets. All the code is
contained within a single file that can be imported using Python's
import mechanism or used as a command-line tool.

The code has been tested with Python 3.7.

Source repository: `<https://github.com/naturhistoriska/cardinality.py>`_

--------------------------------

.. contents:: Table of contents
   :local:
   :backlinks: none


Prerequisites
-------------

* Python 3
* The Python library `pandas <https://pandas.pydata.org>`_

An easy way to get Python working on your computer is to install the free
`Anaconda distribution <http://anaconda.com/download)>`_.


Installation
------------

The project is hosted at `<https://github.com/naturhistoriska/cardinality.py>`
and can be downloaded using git:

.. code-block::

    $ git clone https://github.com/naturhistoriska/cardinality.py


Usage
-----

.. code-block::

	$ ./cardinality.py --help
	usage: cardinality.py [-h] [-V] [-v] [-p column [column ...]]
	                      [-f column [column ...]]
	                      pk-file fk-file

	Command-line utility for examining the cardinality of the relation between two
	TSV-files.

	positional arguments:
	  pk-file               TSV-file with primary keys
	  fk-file               TSV-file with foreign keys

	optional arguments:
	  -h, --help            show this help message and exit
	  -V, --version         show program's version number and exit
	  -v, --verbose         show verbose output
	  -p column [column ...]
	                        primary key columns
	  -f column [column ...]
	                        foreign key columns


Example usage
-------------

Examine the relation between two example datasets included in this repository.

.. code-block::
	
	$ ./cardinality.py test_files/pk-data.tsv test_files/fk-data.tsv -p pk -f fk
	0,1 to 0,3


Running the tests
-----------------

Testing is carried out with `pytest <https://docs.pytest.org/>`_:

.. code-block::

    $ pytest -v test_cardinality.py

Test coverage can be calculated with `Coverage.py
<https://coverage.readthedocs.io/>`_ using the following commands:

.. code-block::

    $ coverage run -m pytest
    $ coverage report -m cardinality.py

The code follow style conventions in `PEP8
<https://www.python.org/dev/peps/pep-0008/>`_, which can be checked
with `pycodestyle <http://pycodestyle.pycqa.org>`_:

.. code-block::

    $ pycodestyle cardinality.py test_cardinality.py


License
-------

``cardinality.py`` is distributed under the 
`MIT license <https://opensource.org/licenses/MIT>`_.


Author and maintainer
---------------------

Markus Englund, markus.englund@nrm.se
