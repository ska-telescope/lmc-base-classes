# -*- coding: utf-8 -*-
#
# This file is part of the RefA project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""Reference Element

SKA Reference Element
"""

from . import release
from . import RefA
from . import RefAchild
from . import RefB
from . import RefBchild
from . import RefMaster
from . import RefTelState
from . import RefAlarms
from . import RefSubarray
from . import RefCapCorrelator
from . import RefCapPssBeams
from . import RefCapPstBeams
from . import RefCapVlbiBeams
from . import FileLogger

from . import Rack
from . import Server
from . import Switch
from . import PDU


__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
