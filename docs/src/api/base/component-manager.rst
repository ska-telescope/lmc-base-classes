======================
Base Component Manager
======================

.. automodule:: ska_tango_base.base.base_component_manager
   :members:

.. py:data:: JSONData

A type hint for any JSON-encodable data.

.. code-block:: py

   JSONData = (
      None
      | bool
      | int
      | float
      | str
      | list["JSONData"]  # A list can contain more JSON-encodable data
      | dict[str, "JSONData"]  # A dict must have str keys and JSON-encodable data
      | tuple["JSONData", ...]  # A tuple can contain more JSON-encodable data
   )
