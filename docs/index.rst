Introduction
============

What is OpenPnPy
----------------

OpenPnPy is a python package implementing Cisco's Network PnP protocol.
It provides a server class, as well as utility functions to easily build PnP XML 
service messages.

To understand what Cisco Network PnP is all about, see 
https://developer.cisco.com/docs/network-plug-n-play/


Basic Usage
-----------

A PnP server with custom behavior can be defined by subclassing the 
:py:class:`openpnpy.server.PnpServer` class, and implementing the handler methods.

Service messages to be returned by the handler methods can be built using functions 
provided by the :py:mod:`openpnpy.messages` module.

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
