# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Literal

from compas.geometry import Line as CLine
from compas.geometry import Point as CPoint
from compas.geometry import intersection_line_line_xy

from axonometry.utils import pair_projections_lines

from .config import config_manager
from .point import Point, is_coplanar, random_point

if TYPE_CHECKING:
    import compas

    from .axonometry import Axonometry
    from .plane import ReferencePlane

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Line:
    """The primary drawing element.

    A line connects two :class:`.Point` objects.

    :param start: The first point.
    :param end: The second point.
    :param data: Optionally set the data on creation, usually handled by
      :py:meth:`~Plane.add_line`.
    :param plane: Optionally set the plane membership on creation, usually set by parent.
    """

    def __init__(
        self,
        start: Point,
        end: Point,
        data: compas.geometry.Line | None = None,
        plane: ReferencePlane | Axonometry | None = None,
    ) -> None:
        assert is_coplanar([start, end]), "Points are not in the same plane."
        # assert start.key != "xyz" and end.key != "xyz" and (start != end), (
        #     "Points are equal, that's not a line."
        # )
        self.plane: ReferencePlane | Axonometry = plane
        """The :py:class:`Plane` of which the line is in; set by parent."""
        self.projections: dict[Literal["xy", "yz", "zx", "xyz"], Line | list[Line]] = {
            "xy": None,
            "yz": None,
            "zx": None,
            "xyz": [],
        }  #: Collection of the lines' projections; updated automatically.
        self.start: Point = start  #: The first point of the line.
        self.end: Point = end  #: The second point of the line.
        self.key: Literal["xy", "yz", "zx", "xyz"] = start.key
        """The lines' coordinate system, i.e. plane membership."""
        self.data: compas.geometry.Line | None = data  #: View plane coordinate system line.

    @property
    def __data__(self) -> dict:
        return {"start": self.start.data.__data__, "end": self.end.data.__data__}

    def __iter__(self):
        """Necessary for compas.geometry functions."""
        return iter([self.start.data, self.end.data])

    def project(
        self,
        distance: float | None = None,
        start_distance: float | None = None,
        end_distance: float | None = None,
        ref_plane_key: Literal["xy", "yz", "zx"] | None = None,
    ) -> Line:
        """Project crurrent line on another plane.

        The projection can be in both directions between one of the three
        :term:`reference planes <Reference plane>` and the
        :term:`axonometric picture plane <Axonometric picture plane>`.

        >>> from axonometry import Axonometry, Point, Line
        >>> my_axo = Axonometry(10,15)

        >>> xy_line = my_axo["xy"].add_line(Line(Point(x=-18, y=6), Point(x=26, y=12)))
        >>> xy_line.project(distance=75)
        Line(Point(x=-18, y=6, z=75), Point(x=26, y=12, z=75))  # z added by projection

        >>> xyz_line = my_axo.add_line(Line(Point(x=6, y=9, z=44), Point(x=45, y=-5, z=9)))
        >>> xyz_line.project(ref_plane_key="yz")
        Line(Point(y=9, z=44), Point(y=-5, z=9))

        :param distance: The missing third coordinate in order to project the line on the
          axonometric picture plane. This applies when the point to project is contained
          in a reference plane.
        :param start_distance: Specify a distinct ``distance`` value for the
          :py:attr:`Line.start` projection.
        :param end_distance: Specify a distinct ``distance`` value for the
          :py:attr:`Line.end` projection.
        :param ref_plane_key: Specify the reference plane for the auxilary projection.
        :return: A new line.
        """
        # determine projection origin plane
        assert self.plane, "To project, the line needs to be part of a plane."
        if self.plane.key == "xyz":
            new_line = self._project_on_reference_plane(ref_plane_key)
        else:
            new_line = self._project_on_axonometry_plane(
                distance,
                start_distance=start_distance,
                end_distance=end_distance,
                ref_plane_key=ref_plane_key,
            )

        return new_line

    def _project_on_axonometry_plane(
        self,
        distance: float,
        start_distance: float | None = None,
        end_distance: float | None = None,
        ref_plane_key: Literal["xy", "yz", "zx"] | None = None,
    ) -> Line:
        """Project line on the axonometric picture plane.

        :param distance: The third coordinate value relative to the current reference plane.
        :param start_distance: Fine-tuning specific distance for beginning of line.
        :param end_distance: Fine-tuning specific distance for end of line.
        """
        # TODO: check if line already exists.

        start_distance = start_distance if start_distance else distance
        end_distance = end_distance if end_distance else distance

        if self.plane.key == "xy":
            new_line = Line(
                Point(x=self.start.x, y=self.start.y, z=start_distance),
                Point(x=self.end.x, y=self.end.y, z=end_distance),
            )  # data will be updated later

            if ref_plane_key is None:
                # Make sure not to use perpendicular plane as auxilary plane
                if self.start.x == self.end.x:
                    ref_plane_key = "yz"
                elif self.start.y == self.end.y:
                    ref_plane_key = "zx"
                else:
                    ref_plane_key = random.choice(["yz", "zx"])  # noqa: S311
            else:
                assert ref_plane_key in ["yz", "zx"], f"Wrong {ref_plane_key=}"

            # Build auxilary line in chosen reference plane
            if ref_plane_key == "yz":
                auxilary_line = self.plane.axo[ref_plane_key].add_line(
                    Line(
                        Point(y=self.start.y, z=start_distance),
                        Point(y=self.end.y, z=end_distance),
                    ),
                )
            elif ref_plane_key == "zx":
                auxilary_line = self.plane.axo[ref_plane_key].add_line(
                    Line(
                        Point(x=self.start.x, z=start_distance),
                        Point(x=self.end.x, z=end_distance),
                    ),
                )

        elif self.plane.key == "yz":
            new_line = Line(
                Point(x=start_distance, y=self.start.y, z=self.start.z),
                Point(x=end_distance, y=self.end.y, z=self.end.z),
            )  # data will be update
            if ref_plane_key is None:
                # Make sure not to use perpendicular plane as auxilary plane
                if self.start.z == self.end.z:
                    ref_plane_key = "xy"
                elif self.start.y == self.end.y:
                    ref_plane_key = "zx"
                else:
                    # Default to XY because dominant in architecture conventions
                    ref_plane_key = "xy"  # random.choice(["zx", "xy"])
            else:
                assert ref_plane_key in ["xy", "zx"], f"Wrong {ref_plane_key=}"

            # Build auxilary line in chosen reference plane
            if ref_plane_key == "zx":
                auxilary_line = self.plane.axo[ref_plane_key].add_line(
                    Line(
                        Point(z=self.start.z, x=start_distance),
                        Point(z=self.end.z, x=end_distance),
                    ),
                )
            elif ref_plane_key == "xy":
                auxilary_line = self.plane.axo[ref_plane_key].add_line(
                    Line(
                        Point(y=self.start.y, x=start_distance),
                        Point(y=self.end.y, x=end_distance),
                    ),
                )

        elif self.plane.key == "zx":
            new_line = Line(
                Point(x=self.start.x, y=start_distance, z=self.start.z),
                Point(x=self.end.x, y=end_distance, z=self.end.z),
            )  # data will be update
            if ref_plane_key is None:
                # Make sure not to use perpendicular plane as auxilary plane
                if self.start.z == self.end.z:
                    ref_plane_key = "xy"
                elif self.start.x == self.end.x:
                    ref_plane_key = "yz"
                else:
                    # Default to XY because dominant in architecture conventions
                    ref_plane_key = "xy"  # random.choice(["xy", "yz"])
            else:
                assert ref_plane_key in ["xy", "yz"], f"Wrong {ref_plane_key=}"

            # Build auxilary line in chosen reference plane
            if ref_plane_key == "xy":
                auxilary_line = self.plane.axo[ref_plane_key].add_line(
                    Line(
                        Point(x=self.start.x, y=start_distance),
                        Point(x=self.end.x, y=end_distance),
                    ),
                )
            elif ref_plane_key == "yz":
                auxilary_line = self.plane.axo[ref_plane_key].add_line(
                    Line(
                        Point(z=self.start.z, y=start_distance),
                        Point(z=self.end.z, y=end_distance),
                    ),
                )

        axo_line_start_data = intersection_line_line_xy(
            CLine.from_point_and_vector(self.start.data, self.plane.projection_vector),
            CLine.from_point_and_vector(
                auxilary_line.start.data,
                self.plane.axo[ref_plane_key].projection_vector,
            ),
        )

        axo_line_end_data = intersection_line_line_xy(
            CLine.from_point_and_vector(self.end.data, self.plane.projection_vector),
            CLine.from_point_and_vector(
                auxilary_line.end.data,
                self.plane.axo[ref_plane_key].projection_vector,
            ),
        )

        new_line.data = CLine(CPoint(*axo_line_start_data), CPoint(*axo_line_end_data))
        new_line.start.data = new_line.data[0]
        new_line.end.data = new_line.data[1]

        self.plane.drawing.add_compas_geometry(
            [
                CLine(self.start.data, axo_line_start_data),
                CLine(auxilary_line.start.data, axo_line_start_data),
                CLine(self.end.data, axo_line_end_data),
                CLine(auxilary_line.end.data, axo_line_end_data),
            ],
            layer_id=config_manager.config["layers"]["projection_traces"]["id"],
        )

        self.plane.axo.add_line(new_line)
        pair_projections_lines(new_line, auxilary_line)
        pair_projections_lines(new_line, self)

        return new_line

    def _project_on_reference_plane(
        self,
        ref_plane_key: Literal["xy", "yz", "zx"],
    ) -> Line:
        """Project the line on the selected reference plane.

        Knowing that the current line is member of the axo plane.
        """
        if self == self.projections[ref_plane_key]:
            # projection of line already exists, nothing to do
            logger.debug("Line already exists.")
            new_line = self.projections[ref_plane_key]
        else:
            if ref_plane_key == "xy":
                new_line = self.plane[ref_plane_key].add_line(
                    Line(
                        Point(x=self.start.x, y=self.start.y),
                        Point(x=self.end.x, y=self.end.y),
                    ),
                )
            elif ref_plane_key == "yz":
                new_line = self.plane[ref_plane_key].add_line(
                    Line(
                        Point(y=self.start.y, z=self.start.z),
                        Point(y=self.end.y, z=self.end.z),
                    ),
                )
            elif ref_plane_key == "zx":
                new_line = self.plane[ref_plane_key].add_line(
                    Line(
                        Point(x=self.start.x, z=self.start.z),
                        Point(x=self.end.x, z=self.end.z),
                    ),
                )

            # draw new projection line
            self.plane.drawing.add_compas_geometry(
                [
                    CLine(self.start.data, new_line.start.data),
                    CLine(self.end.data, new_line.end.data),
                ],
                layer_id=config_manager.config["layers"]["projection_traces"]["id"],
            )

            pair_projections_lines(self, new_line)

        return new_line

    def project_into_axo_surface(self, distance: float, length: float) -> None:
        """Projection of a surface in axonometric picture plane out of its perpendicular lines."""
        logger.info(f"{self.start.data=};{self.end.data=}")
        assert self.key != "xyz", (
            "Only possible to project from reference plane into axonometric picture plane."
        )

        def _get_projection_planes(line):
            keys = [key for key, val in line.projections.items() if isinstance(val, Line)]
            return keys

        new_line_1 = self.start.project_into_axo_line(distance=distance, length=length)
        aux_planes = _get_projection_planes(new_line_1)
        new_line_2 = self.end.project_into_axo_line(
            distance=distance,
            length=length,
            ref_plane_keys=aux_planes,
        )
        self.plane.axo.add_line(Line(new_line_1.start, new_line_2.start))
        self.plane.axo.add_line(Line(new_line_1.end, new_line_2.end))

        logger.info(f"{new_line_2.projections=}")
        logger.info(f"{new_line_1.projections=}")

        # logger.info(f"{new_line_1.data=}")
        # logger.info(f"{new_line_2.data=}")

    def __eq__(self, other: Line) -> bool:
        """Lines are equal when their points are equal."""
        if (not isinstance(other, type(self))) or (self is None or other is None):
            # if the other item of comparison is not also of the Point class
            return False
        return (self.start == other.start and self.end == other.end) or (
            self.start == other.end and self.end == other.start
        )

    def __repr__(self) -> str:
        """Made of points."""
        return f"Line({self.start}, {self.end})"


def random_line(key: Literal["xy", "yz", "zx", "xyz"] = "xyz") -> Line:
    """Make a random line object, perpendicular to one of the coordinate planes."""
    if key == "xy":
        start = random_point("xy")
        end = random.choice(  # noqa: S311
            [
                Point(x=start.x + random.randint(10, 50), y=start.y),  # noqa: S311
                Point(x=start.x, y=start.y + random.randint(10, 50)),  # noqa: S311
            ],
        )
    elif key == "yz":
        start = random_point("yz")
        end = random.choice(  # noqa: S311
            [
                Point(z=start.z + random.randint(10, 50), y=start.y),  # noqa: S311
                Point(z=start.z, y=start.y + random.randint(10, 50)),  # noqa: S311
            ],
        )
    elif key == "zx":
        start = random_point("zx")
        end = random.choice(  # noqa: S311
            [
                Point(z=start.z + random.randint(10, 50), x=start.x),  # noqa: S311
                Point(z=start.z, x=start.x + random.randint(10, 50)),  # noqa: S311
            ],
        )
    elif key == "xyz":
        start = random_point()
        end = random.choice(  # noqa: S311
            [
                Point(z=start.z + random.randint(10, 50), x=start.x, y=start.y),  # noqa: S311
                Point(z=start.z, x=start.x + random.randint(10, 50), y=start.y),  # noqa: S311
                Point(z=start.z, x=start.x, y=start.y + random.randint(10, 50)),  # noqa: S311
            ],
        )
    return Line(start, end)
