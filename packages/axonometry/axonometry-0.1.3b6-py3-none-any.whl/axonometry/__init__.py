# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""A toolbox to script and generate axonometric drawing operations.

To enable a maximum amount of thinkering, the following API documentation
covers all public objects of the codebase. For scripting,
the :py:class:`Axonometry`, :py:class:`Point` and :py:class:`Line`
classes and their corresponding methods are sufficient.
"""

from __future__ import annotations

from .axonometry import *  # noqa: F403
from .config import ConfigManager
from .drawing import *  # noqa: F403
from .line import *  # noqa: F403
from .plane import *  # noqa: F403
from .point import *  # noqa: F403
from .trihedron import *  # noqa: F403
from .utils import *  # noqa: F403
