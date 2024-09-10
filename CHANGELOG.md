# Changelog

## unreleased

- Add new `invoke_lrc` function as a callback API for LRCs (WOM-369, WOM-393, WOM-394).
- Documentation: (WOM-366, WOM-373)
  - Update logging guide from README and add it to ReadTheDocs.
  - Add documentation for the `communication_state_callback` and `component_state_callback` keyword arguments of a component manager.
- Housekeeping:
  - WOM-365: Remove unnecessary typing_extensions import.

## 1.0.0

- Breaking changes:
  - WOM-299: Update to pytango ^9.4.2 for build and 9.5.0 for development.
  - Update to ska-control-model 1.0.0 (REL-1292) - this removes `adminMode.MAINTENANCE`.
  - WOM-250, WOM-345: Remove `max_workers` from `TaskExecutorComponentManager`.
  - WOM-343: Update TaskExecutor to follow TaskStatus state machine.
    - Long Running Commands are transitioned to `TaskStatus.STAGING` initially.
    - When in a final status, all tasks have a result of the form `(ResultCode, message)`.
- Other changes to the Long Running Command and related attributes:
  - WOM-302: Set correct LRC attribute spectrum limits.
    - If there are too many items to report for `longRunningCommandStatus`, `longRunningCommandsInQueue` and `longRunningCommandIDsInQueue`, the oldest completed commands are now pruned from the list and a warning is logged.
    - `longRunningCommandInProgress` now supports reporting multiple commands in progress. If there are no commands in progress, this attribute now returns an empty list instead of `["", ""]`.
  - WOM-342: Made `max_queued_tasks` and `max_executing_tasks` read only attributes that have hard-coded values for the different base classes.
- Documentation: (WOM-300, WOM-357, WOM-358)
  - Restructured and revised all the documentation, split into how-to, explanation and reference. 
  - Added [1.0.0 migration guide](https://developer.skao.int/projects/ska-tango-base/en/latest/releases/migrating-to-1.0.html) explaining all the breaking changes listed above in more detail.
  - Fixed long outstanding issues with API auto generated docs.

## 0.20.2

- WOM-319: Fix timing issue with LRCInProgress and `Abort()`
- WOM-320: Do not directly call Tango operations while holding the `CommandTracker` lock

## 0.20.1

- WOM-273: Pin poetry version in readthedocs.yml
- WOM-274: Mark tests where `Abort()` is used as xfail

## 0.20.0

- WOM-265: Deprecate `max_workers` for `TaskExecutorComponentManager`
- WOM-266: Revert LRC attribute size to 64 queued commands
- WOM-211: Add `commandedState` and `commandedObsState` attributes
- MCCS-1993: Update to use latest version of ska-control-model
- WOM-212: Add `longRunningCommandInProgress` attribute

## 0.19.3

- WOM-213: Limit input queue size for long running commands
- WOM-177: Fix `push_change_event` and `push_archive_event` to expose the official PyTango interface

## 0.19.2

- LOW-614: Remove `DevInt`, removed in cppTango/PyTango 9.5.0
- KAR-585: Improve docs to reflect input queue updates

## 0.19.1

- MCCS-1695: Workaround for pytango 9.4.2 logging interface change

## 0.19.0

- MCCS-1636: Use ska-ser-sphinx-theme for documentation
- KAR-632: Unpinned numpy requirements. Bumped minimum Python version to 3.8
- KAR-587: Input queue updates

## 0.18.1

- MCCS-1494: Bug fixes to subarray subclassing following addition of JSON validation support
- KAR-497: Further task callback parameters bug fixes
- MCCS-1579: Strict type-checking, leading to bug fixes in task callback parameters
  and subarray resource pool checking

## 0.18.0

- MCCS-1424: JSON validation support

## 0.17.0

- MCCS-1358: Remove CSP-specific content (into separate ska-csp-lmc-base repo)

## 0.16.1

- LOW-418: Remove redundant production Dockerfile, relax pytango constraint
- LOW-415: Complete linting and type-hinting

## 0.16.0

- MCCS-1312: Update to pytango 9.3.6

## 0.15.0

- MCCS-1208: Allow `Abort()` from RESOURCING, `Off()` from FAULT

## 0.14.0

- LOW-346: Provide polling mechanism as alternive concurrency mechanism
  to task executor

## 0.13.6

- Updated numpy version

## 0.13.5

- REL-275: Fix pipeline

## 0.13.4

- KAR-466: Repository maintenance
- MCCS-1072: Type hint & static type check base class alarm_handler_device & utils
- MCCS-934: Type hint & Static type check base classes
- LOW-330: Import control model definitions from ska-control-model
- LOW-317: Allow `Reset()` from STANDBY and ON states, not just FAULT

## 0.13.3

- KAR-403: Fixed exceptions in LRCs not updating  `longRunningCommandResult` accordingly
- LOW-299: Fixed docs build in the CI pipeline
- LOW-278: Now using ska-tango-testing
- SAH-1156: Enable `assigned_resources` property inside `SubarrayComponentManager`.

## 0.13.2

- CT-738: fix check long running status
- AT3-140: fix base TANGO xmi files
- MCCS-1053: Fix the problem of device in UNKNOWN state upon test startup
- PERENTIE-1350: Remove misleading `CspSubarrayComponentManager.__init__` function

## 0.13.1

- KAR-399: Renamed `SKAController` command `isCapabilityAchievable` to `IsCapabilityAchievable`.

## 0.13.0

- MCCS-876: Updated implementation of long running commands
  - SAR-341: Updated docs
  - SAR-351: Updated tests

## 0.12.1

- SAR-303
  - Fixed PYPI URL
  - Moved command response message to component manager
- MCCS-845
  - `NO_SUPPLY` added to `PowerMode` enum

## 0.12.0

- Implemented ST-946 (automation templates)
- Included Long running commands implementation
  - SAR-277, SAR-287, SAR-286, SAR-276, SAR-275, SAR-273

## 0.11.3

- No change, moving artefacts to a new [Central Aftefact Repository](https://artefact.skao.int/).

## 0.11.2

- Update docstrings for 100% coverage and PEP257 compliance

## 0.11.1

- Minor breaking change: rename of "Master" devices to "Controller"

## 0.11.0

- Breaking change: state models and component managers
  - Re-implementation of operational state model to better model
    hardware and support device decoupling.
  - Decoupling of state models from each other
  - Introduction of component managers, to support component monitoring
- Update to latest containers
- Add developer guide to documentation

## 0.10.1

- Make dependency on `pytango` and `numpy` python packages explicit.
- Add optional "key" parameter to `SKASubarrayResourceManager` to filter JSON for
  assign & release methods.

## 0.10.0

- Add `DebugDevice` command to `SKABaseDevice`.  This allows remote debugging to be
  enabled on all devices.  It cannot be disabled without restarting the process.
  If there are multiple devices in a device server, debugging is only enabled for
  the requested device (i.e., methods patched for debugging cppTango threads).
  However, all Python threads (not cppTango threads), will also be debuggable,
  even if created by devices other than the one that was used to enable debugging.
  There is only one debugger instance shared by the whole process.
  
## 0.9.1

- Changed dependency from `ska_logging` to `ska_ser_logging`.

## 0.9.0

- Breaking change: Package rename
  - Installable package name changed from `lmcbaseclasses` to `ska_tango_base`.
  - Package import `ska.base` has been changed to `ska_tango_base`.  For example, instead of
    `from ska.base import SKABaseDevice` use `from ska_tango_base import SKABaseDevice`.

## 0.8.1

- Fix broken docs

## 0.8.0

- Add base classes for CSP SubElements

## 0.7.2

- Switch to threadsafe state machine

## 0.7.1

- Bugfix for `Reset()` command

## 0.7.0

- Separate `adminMode` state machine from `opState` state machine
- Add support for STANDBY `opState`
- Add `Standby()` and `Disable()` commands to `SKABaseDevice`
- Breaking behavioural changes to adminMode and `opState` state machines
- Breaking change to `_straight_to_state` method signature

## 0.6.6

- Documentation bugfix

## 0.6.5

- Fix to observation state machine: allow `Abort()` from RESETTING observation
  state

## 0.6.4

- Refactor state machine to use pytransitions library.
- Minor behavioural change:` Off()` command is accepted in every obsState, rather
than only EMPTY obsState.
- support `_straight_to_state` shortcuts to simplify test setups
- Refactor of state machine testing to make it more portable

## 0.6.3

- Fix omission of `fatal_error` transition from base device state machine.

## 0.6.2

- Fix issue with incorrect updates to transitions dict from inherited devices.
  Only noticeable if running multiple devices of different types in the same
  process.

## 0.6.1

- Add `ON` state to `SKABaseDeviceStateModel`.
- Move `On()` and `Off()` commands to `SKABaseDevice`.
- Add event pushing for device state, device status, admin mode and obs state
  (change and archive events).
- Disable all attribute polling.

## 0.6.0

- Breaking change: State management
  - `SKABaseDevice` implements a simple state machine with states
    `DISABLED`, `OFF`, `ON`, `INIT` and `FAULT`, along with transitions
    between them.
  - `SKASubarray` implements full subarray state machine in accordance
    with ADR-8 (the underlying state model supports all states and
    transitions, including transitions through transient states; the
    subarray device uses this state model but currently provide a
    simple, purely synchronous implementation)
  - Base classes provide subclassing code hooks that separate management
    of device state from other device functionality. Thus, subclasses
    are encouraged to leave state management in the care of the base
    classes by:
    - leaving `init_device()` alone and placing their (stateless)
      initialisation code in the `do()` method of the `InitCommand` object instead. The base `init_device()` implementation will ensure that
      the `do()` method is called, whilst ensuring state is managed e.g.
      the device is put into state `IDLE` beforehand, and put into the
      right state afterwards.
    - leaving commands like `Configure()` alone and placing their
      (stateless) implementation code in `ConfigureCommand.do()`
      instead. This applies to all commands that affect device state:
       `Off()`, `On()`, `AssignResources()`, `ReleaseResources()`,
       `ReleaseAllResources()`, `Configure()`, `Scan()`, `EndScan()`,
       `End()`, `Abort()`, `Reset()`, `Restart()`.
    - leaving the base device to handle reads from and writes to the
      state attributes `adminMode`, `obsState` and device `state`. For
      example, do not call `Device.set_state()` directly; and do not
      override methods like `write_adminMode()`.

## 0.5.4

- Remove `ObsState` command from `SKACapability`, `SKAObsDevice` and `SKASubarray` Pogo XMI files.  It should not
  have been included - the `obsState` attribute provides this information. The command was not in the Python
  files, so no change to usage.  It only affects future Pogo code generation.
- Add new logging target, `"tango::logger"`, that forwards Python logs to the Tango Logging Service.  This
  is enabled by default in code, but could be overridden by existing Tango Database device properties.
- Maximum number of logging targets increased from 3 to 4.

## 0.5.3

- Setting `loggingTargets` attribute to empty list no longer raises exception.
- Change syslog targets in `loggingTargets` attribute to a full URL so that remote syslog servers can be specified.
  For example, `"syslog::udp://server.domain:514"`, would send logs to `server.domain` via UDP port 514.
  Specifying a path without a protocol, like `"syslog::/var/log"`, is deprecated.

## 0.5.2

- Change ska_logger dependency to use ska-namespaced package (v0.3.0).  No change to usage.

## 0.5.1

- Make 'ska' a [native namespace package](https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages).
  No change to usage.

## 0.5.0

- Breaking change:  Major restructuring of the package to simplify imports and reduce confusion.
  - The single word `skabase` module has now changed to two words: `ska.base`.
  - Instead of `from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice` to import the
    class, just use `from ska.base import SKABaseDevice`.
  - Instead of `skabase.control_model` use `ska.base.control_model`.
  - The `SKATestDevice` was removed.  Note that this class was only intended
    for internal use and is no longer needed.
  - Removed unused scripts and modules.
- Removed `TangoLoggingLevel` which was deprecated in 0.4.0.  Use `ska.base.control_model.LoggingLevel`
  instead.

## 0.4.1

- Fix lost properties when re-initialising test device (remove `get_name` mock).
- Fix Sphinx doc building.
- Move `ObsDevice` variable initialisation from `__init__` to `init_device`.
- Run scripts with `python3` instead of `python` and update pip usage.

## 0.4.0

- Changed all `DevEnum` attributes to use Python `enum.IntEnum` classes.  These can be imported from the
  new `control_model` namespace, e.g., `skabase.control_model import AdminMode`.
- The names of some of the enumeration labels were changed to better match the Control Systems Guidelines.
  - `ON-LINE` changed to `ONLINE`.
  - `OFF-LINE` changed to `OFFLINE`.
  - All dashes were changed to underscores to allow usage as Python variables.
- Changed `simulationMode` attribute from `bool` to enumerated type: `SimulationMode`.
- Changed `testMode` attribute from `str` to enumerated type: `TestMode`.
- Deprecated `TangoLoggingLevel`.  Will be removed in version 0.5.0.  Use `skabase.control_model.LoggingLevel`
  instead.
- Remove unnecessary usage of `DeviceMeta` class.

## 0.3.1

- Used `ska_logging` library instead of defining logging format and handlers locally.
- `LoggingTargetDefault` property is now empty instead of `"console::cout"`, since the
  the `ska_logging` library will automatically output to stdout.
- Fixed device name field in log message if a device server includes multiple devices.
- Removed a number of unused files in the `ansible` and `refelt` folders.

## 0.3.0

- Not released

## 0.2.0

- Changed logging to use SKA format
- Simplified element, storage and central logging to just a single target.  Default writes to stdout.
  This is in line with the move to Elastic for all logs instead of using the Tango Logging Service
  for some cases.
- Deprecated `dev_logging` method.  Will be removed in 0.3.0.  Use direct calls the `self.logger` instead.

## 0.1.3

- Storage logs are written to a file if Syslog service is not available.
- Added exception handling
- Improved code coverage
- Improved compliance to coding standards
- Improvement in documentation
- Other minor improvements

## 0.1.2

- Internal release

## 0.1.1

- Logging functionality
- Python3 migration
- Repackaging of all the classes into a single Python package
- Changes to folder structure,
- Integration in CI environment