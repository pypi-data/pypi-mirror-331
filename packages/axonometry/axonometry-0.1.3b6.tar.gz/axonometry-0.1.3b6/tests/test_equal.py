# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import random
import unittest

from axonometry import Axonometry, Point, config_manager
from axonometry.utils import random_valid_angles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometryEqualities(unittest.TestCase):

    def setUp(self):
        self.x, self.y, self.z = [random.random() for _ in range(3)]
        self.alpha, self.beta = random_valid_angles()
        self.axo = Axonometry(self.alpha, self.beta)
        self.p0 = self.axo.add_point(Point(x=self.x, y=self.y, z=self.z))
        self.p1 = self.axo["xy"].add_point(Point(x=self.x, y=self.y))
        self.p2 = self.axo["yz"].add_point(Point(y=self.y, z=self.z))
        self.p3 = self.axo["zx"].add_point(Point(z=self.z, x=self.x))

    def test_point_equalities(self):
        self.assertEqual(self.p0, self.p1)
        self.assertEqual(self.p0, self.p2)
        self.assertEqual(self.p0, self.p3)
        self.assertEqual(self.p0, self.p1.project(distance=self.z))
        self.assertEqual(self.p0, self.p2.project(distance=self.x))
        self.assertEqual(self.p0, self.p3.project(distance=self.y))
        self.assertEqual(self.p1, self.p0.project(ref_plane_key="xy"))
        self.assertEqual(self.p2, self.p0.project(ref_plane_key="yz"))
        self.assertEqual(self.p3, self.p0.project(ref_plane_key="zx"))


if __name__ == "__main__":
    unittest.main()
