=========
MinerAPI
=========

Python wrapper for the miners RPC API (`cgminer <https://github.com/ckolivas/cgminer>`_/`bfgminer <https://github.com/luke-jr/bfgminer>`_, `cpuminer-multi <https://github.com/tpruvot/cpuminer-multi>`_).

This is a fork of `pycgminer <https://github.com/tsileo/pycgminer>`_ by Thomas Sileo.


Installation
------------

.. code-block::

    $ pip install minerapi


QuickStart
----------

.. code-block:: python

    from minerapi import Cgminer

    cgminer = Cgminer()

    summary = cgminer.summary()

    my_asic = cgminer.asc(0)
