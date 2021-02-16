.. SKA Tango Base documentation master file, created by
   sphinx-quickstart on Fri Jan 11 10:03:42 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. |br| raw:: html

   <br />

SKA CSP Sub-element ObsDevice
============================================

.. toctree::
   :maxdepth: 2

.. automodule:: ska_tango_base.csp_subelement_obsdevice
.. autoclass:: ska_tango_base.CspSubElementObsDevice
   :members:
   :undoc-members:


Instance attributes
-------------------
Here it is reported the list of the *instance attributes*. |br|

* ``scan_id``: the identification number of the scan. |br|
  The scan ID is passed as argument of the *Scan* command. |br|
  The attribute value is reported via TANGO attribute *scanID*.

* ``_sdp_addresses``: a python dictionary with the SDP destination addresses for the output
  products. |br|
  Depending on the sub-element (CBF, PSS, PST) this attribute can specify more than one destination address,
  as for example in CBF sub-element. |br|
  The SDP destination addresses are specified at configuration.
  An SDP address specifies the MAC address, IP address and port of the endpoint. |br|
  Below an example of how SDP addresses are specified in a Mid CBF configuration::

        {
          ...
          "outputHost": [[0, "192.168.0.1"], [8184, "192.168.0.2"]],
          "outputMac": [[0, "06-00-00-00-00-01"]],
          "outputPort": [[0, 9000, 1], [8184, 9000, 1]]
          ...
        }

  The value of this attribute is reported via the TANGO *sdpDestionationAddresses* attribute.

  .. note::  Not all the Sub-element observing devices are connected to the SDP (for example Mid VCCs).


* ``_sdp_links_active``: a python list of boolean. Each list element reports the network connectivity of the
  corresponding link to SDP.

* ``_sdp_links_capacity``: this attribute records the capacity in GB/s of the SDP link.

* ``_config_id``: it stores the unique identificator associated to a JSON scan configuration. |br|
  The value of this attribute is reported via the TANGO attriute *configID*.

* ``_last_scan_configuration``: this attribute stores the last configuration successully programmed. |br|
  The value is reported via the TANGO attribute *lastScanConfiguration*.


* ``_health_failure_msg``:
  The value is reported via the TANGO attribute *healthFailureMesssage*.
