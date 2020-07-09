.. LMC Base Classes documentation master file, created by
   sphinx-quickstart on Fri Jan 11 10:03:42 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SKA BaseDevice
============================================

The SKABaseDevice implements the basic device state machine, as illustrated
below, but without, at present, a Standby state.

.. image:: images/device_state_diagram.png
  :width: 400
  :alt: Diagram of the device state machine showing states and transitions


.. toctree::
   :maxdepth: 2

.. automodule:: ska.base.base_device
.. autoclass:: ska.base.SKABaseDevice
   :members:
   :undoc-members:
