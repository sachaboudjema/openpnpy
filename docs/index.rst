Introduction
============

OpenPnPy is a python package implementing the Cisco Network PnP protocol.
It provides a server class to establish communication with PnP agents, as well as
utility functions to easily build PnP XML service messages.

A very basic server implementation could look like this:

.. literalinclude:: example_server.py
   :language: python

Which can then be run like so:

.. code-block:: shell

   python3 myserver.py


.. toctree::
   :hidden:
   :maxdepth: 4

   self
   api
