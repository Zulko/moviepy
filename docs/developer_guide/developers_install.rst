.. _developers_install:

Installation for MoviePy developers
======================================

.. warning::
    This part is only destined to people who want to build the MoviePy documentation by themselves, or to contribute to MoviePy. Normal users don't need it.

In addition to MoviePy main libraries, MoviePy developers will also need to install additional libraries to be able to run MoviePy tests and build the MoviePy documentation.

Libraries for documentation
-----------------------------

You can install the libraries required to build documentation with: 

.. code:: bash

    $ (sudo) pip install moviepy[doc]

Once libraries installed you can build the documentation with:

.. code:: bash

    $ python setup.py build_docs


Libraries for testing and linting
-------------------------------------

You can install the libraries required for testing and linting with:

.. code:: bash

    $ (sudo) pip install moviepy[test]
    $ (sudo) pip install moviepy[lint]

Once libraries installed you can test with:

.. code:: bash

    $ python -m pytest

And you can lint with:

.. code:: bash

    $ python -m black .




