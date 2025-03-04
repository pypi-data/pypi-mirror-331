# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Surface:
    """To be implemented soon."""

    def __init__(self) -> None:
        self.plane = None  # set by parent
        self.projections = {"xy": None, "yz": None, "zx": None, "xyz": []}
