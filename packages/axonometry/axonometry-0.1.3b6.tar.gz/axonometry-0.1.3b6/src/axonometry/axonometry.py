# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import math
import pathlib
from typing import TYPE_CHECKING, Literal

from .config import config_manager
from .drawing import Drawing
from .plane import Plane, ReferencePlane
from .trihedron import Trihedron
from .utils import random_valid_angles, save_svg, show_paths, visualize

if TYPE_CHECKING:
    from compas.geometry import Vector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Axonometry(Plane):
    """Axonometry by intersection setup.

    This class helps to set up the axonometry. From there one can start to use its
    method to add geometries (mostly :py:class:`Line`).

    To set up the necessary projection planes, the class first instatiates a
    :py:class:`Trihedron` object which calculates the :term:`tilt <Tilt>` to produce the three
    :py:class:`ReferencePlane` objects. These, and the :py:class:`Axonometry` can then be used
    to draw, i.e. :py:meth:`~Plane.add_line`.

    As an attribute, this class instantiates a :py:class:`Drawing` object which collects, or
    so to say records, all the drawing and projection operations (:py:meth:`~Plane.add_line`,
    :py:meth:`~Line.project`).

    .. note::

        When adding objects, and they have only two of the x y z, it means they are projecitons
        in a reference plane.

    :param angles: Architectural notation axonometry angle pair.
    :param trihedron_position: Position of trihedron on the paper.
    :param ref_planes_distance: Reference plane transolation distance.
    :param trihedron_size: Coordinate axes size.
    """

    def __init__(
        self,
        *angles: float,
        trihedron_position: tuple[float, float] = (0, 0),
        ref_planes_distance: float = 100.0,
        trihedron_size: float = 100.0,
        page_size: Literal["A1"] | tuple[float, float] = "A1",
        orientation: str = "portrait",
    ) -> None:
        super().__init__()  # Access methods of the parent class
        Plane.drawing = Drawing(page_size=page_size, orientation=orientation)
        """Instantiate Drawing object for all Plane objects."""
        ReferencePlane.axo = self
        """Attribute this Axonometry object to all ReferencePlane objects."""
        self.key = "xyz"
        logger.info(f"[AXONOMETRY] {angles[0]}°/{angles[1]}°")
        self._trihedron = Trihedron(
            tuple(angles),
            position=trihedron_position,
            size=trihedron_size,
            ref_planes_distance=ref_planes_distance,
        )

        Plane.drawing.add_compas_geometry(
            self._trihedron.axes.values(),
            layer_id=config_manager.config["layers"]["axo_system"]["id"],
        )
        for plane in self._trihedron.reference_planes.values():
            Plane.drawing.add_compas_geometry(
                plane.axes,
                layer_id=config_manager.config["layers"]["axo_system"]["id"],
            )

    @property
    def x(self) -> Vector:
        """X coordinate vector."""
        return self._trihedron.axes["x"].direction

    @property
    def y(self) -> Vector:
        """Y coordinate vector."""
        return self._trihedron.axes["y"].direction

    @property
    def z(self) -> Vector:
        """Z coordinate vector."""
        return self._trihedron.axes["z"].direction

    @property
    def xy(self) -> ReferencePlane:
        """XY reference plane."""
        return self._trihedron.reference_planes["xy"]

    @property
    def yz(self) -> ReferencePlane:
        """YZ reference plane."""
        return self._trihedron.reference_planes["yz"]

    @property
    def zx(self) -> ReferencePlane:
        """ZX reference plane."""
        return self._trihedron.reference_planes["zx"]

    def show_paths(self) -> None:
        """Display the drawing paths with the :py:mod:`vpype_viewer`."""
        show_paths(self)

    def visualize(self) -> None:
        """Not Implemented."""
        visualize(self)

    def save_svg(self, filename: str, directory: str = "./output/") -> None:
        """Save drawing to file.

        TODO: check best pracatice for file location.

        :param filename: Name of the SVG file.
        :param directory: Path to directory, defaults to ``./output/``.
        """
        try:
            with pathlib.Path.open(directory + filename + ".svg", "w") as f:
                save_svg(self, f)
        except FileExistsError:
            logger.info("Already exists.")

    def _save_json(self, filename: str, directory: str = "./output/") -> None:
        """Save drawing data to json file."""
        try:
            with pathlib.Path.open(directory + filename + ".json", "w") as f:
                Plane.drawing.save_json(f)
        except FileExistsError:
            logger.info("Already exists.")

    def __repr__(self) -> str:
        """Get axonometry values in standard horizon angle notation."""
        return f"Axonometry {math.degrees(self._trihedron.axo_angles[0]):.2f}°/{math.degrees(self._trihedron.axo_angles[1]):.2f}°"

    def __getitem__(self, item: str) -> ReferencePlane:
        """Select a reference plane by key."""
        if item in self._trihedron.reference_planes:
            return self._trihedron.reference_planes[item]
        return self

    @staticmethod
    def random_angles() -> Axonometry:
        """Generate valid axonometric angles and initialize the Axonometry object."""
        angles = random_valid_angles()
        return Axonometry(*angles)
