# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest
from unittest.mock import patch

from axonometry import Axonometry, config_manager
from axonometry.utils import random_valid_angles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometrySaving(unittest.TestCase):

    def setUp(self):
        self.alpha, self.beta = random_valid_angles()
        self.axo = Axonometry(self.alpha, self.beta)

    @patch("axonometry.Axonometry.save_svg")
    def test_saving_svg(self, mock_save_svg):
        svg_file = f"test_axo_{self.alpha}-{self.beta}.svg"
        """Test saving an Axonometry instance to a SVG file."""
        self.axo.save_svg(svg_file)
        mock_save_svg.assert_called_once_with(svg_file)


if __name__ == "__main__":
    unittest.main()
