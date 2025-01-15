========================
How to use OpenTelemetry
========================

Since version 10.0.0, PyTango provides support for distributed tracing and logging via 
the `OpenTelemetry <https://opentelemetry.io/docs/what-is-opentelemetry/>`_ framework. 
PyTango 10.0.0 and OpenTelemetry can be used with ska-tango-base since version 1.3.0.

In order to enable automatic OpenTelemetry traces (or to add your own), ska-tango-base
must be installed with the optional OpenTelemetry SDK packages by specifying the 
'telemetry' extra option in poetry like this::

    [tool.poetry.dependencies]
    ska-tango-base = { version = "^1.3.0", extras = ["telemetry"] }


You will also have to set the following environment variable to enable telemetry::

    TANGO_TELEMETRY_ENABLE=on

Tango device servers and proxies will then emit automatic traces to stdout. To collect
traces with another service, or add custom traces, refer to the latest `PyTango how-to
guides <https://tango-controls.readthedocs.io/projects/pytango/en/latest/how-to/telemetry.html>`_.

Here is an example of an automatic C++ Tango trace for a command::

    {
        name          : virtual CORBA::Any* Tango::Device_4Impl::command_inout_4(const char*, const CORBA::Any&, Tango::DevSource, const Tango::ClntIdent&)
        trace_id      : 55a7da70649618afb6814818f6a2682c
        span_id       : bf73a95ae7dccdd2
        tracestate    :
        parent_span_id: 9c16ea3625f7ee73
        start         : 1736952808692156238
        duration      : 1158502
        description   : 
        span kind     : Server
        status        : Unset
        attributes    : 
            tango.operation.argument: On
        events        : 
        links         : 
        resources     : 
            telemetry.sdk.version: 1.16.1
            telemetry.sdk.language: cpp
            tango.host: 
            tango.process.kind: server
            telemetry.sdk.name: opentelemetry
            service.instance.id: foo/bar/2
            tango.process.id: 99391
            service.name: ReferenceSkaBaseDevice
            tango.server.name: ReferenceSkaBaseDevice/test
            service.namespace: tango
        instr-lib     : tango.cpp-10.0.0
    }

Here is an example of an automatic PyTango trace for a command::

    {
        "name": "SKABaseDevice.On",
        "context": {
            "trace_id": "0x55a7da70649618afb6814818f6a2682c",
            "span_id": "0x3e1f01c84bca6606",
            "trace_state": "[]"
        },
        "kind": "SpanKind.SERVER",
        "parent_id": "0xbf73a95ae7dccdd2",
        "start_time": "2025-01-15T14:53:28.692561Z",
        "end_time": "2025-01-15T14:53:28.693137Z",
        "status": {
            "status_code": "UNSET"
        },
        "attributes": {
            "code.filepath": "/workspaces/ska-tango-base/src/ska_tango_base/base/base_device.py",
            "code.lineno": 1569,
            "thread.id": "0x7fca437fe640",
            "thread.name": "Dummy-2"
        },
        "events": [],
        "links": [],
        "resource": {
            "attributes": {
                "telemetry.sdk.language": "python",
                "telemetry.sdk.name": "opentelemetry",
                "telemetry.sdk.version": "1.29.0",
                "host.name": "536f9795bc3f",
                "service.namespace": "tango",
                "service.name": "ReferenceSkaBaseDevice",
                "service.instance.id": "foo/bar/2"
            },
            "schema_url": ""
        }
    }