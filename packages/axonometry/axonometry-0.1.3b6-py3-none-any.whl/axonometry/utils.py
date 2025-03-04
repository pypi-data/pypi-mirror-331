# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Literal

from compas.geometry import Geometry as CGeometry
from compas.geometry import Line as CLine
from compas.geometry import Point as CPoint
from compas.geometry import Polyline as CPolyline
from shapely import LineString
from vpype import Document, LineCollection, circle, read_svg, write_svg
from vpype_cli import execute

from .config import config_manager

if TYPE_CHECKING:
    from .axonometry import Axonometry
    from .line import Line
    from .point import Point


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _convert_compas_to_shapely(compas_geometry: CGeometry) -> LineString:
    """Convert a compas geometry object to a shapely LineString."""
    if isinstance(compas_geometry, CLine):
        return LineString(
            [
                (
                    compas_geometry.start.x * config_manager.config["css_pixel"],
                    compas_geometry.start.y * config_manager.config["css_pixel"],
                ),
                (
                    compas_geometry.end.x * config_manager.config["css_pixel"],
                    compas_geometry.end.y * config_manager.config["css_pixel"],
                ),
            ],
        )
    if isinstance(compas_geometry, CPolyline):
        return LineString(
            [
                (
                    point.x * config_manager.config["css_pixel"],
                    point.y * config_manager.config["css_pixel"],
                )
                for point in compas_geometry
            ],
        )
    if isinstance(compas_geometry, CPoint):
        if config_manager.config["point_radius"]:
            return circle(
                compas_geometry.x * config_manager.config["css_pixel"],
                compas_geometry.y * config_manager.config["css_pixel"],
                config_manager.config["point_radius"],
            )
        return None
    raise ValueError(f"Unsupported Compas geometry type: {compas_geometry}")


def _convert_svg_vpype_doc(svg_file: str) -> Document:
    """Create a vpype Document from a list of Compas geometries."""
    coll = read_svg(svg_file, 0.01)[0].as_mls()
    points = []
    for line in coll.geoms:
        for coord in line.coords:
            points.append(coord)

    compas_geometries = [CPolyline(points)]
    layers = convert_compas_to_vpype_lines(compas_geometries)
    document = Document()
    for layer in layers:
        document.add(layer, layer_id=1)  # Assuming all lines are on the same layer
    return document


def convert_compas_to_vpype_lines(
    compas_geometries: list[CGeometry],
) -> LineCollection:
    """Convert a list of compas geometries to a vpype :py:class:`vpype.LineCollection`."""
    vpype_lines = LineCollection()
    for compas_geometry in compas_geometries:
        shapely_line = _convert_compas_to_shapely(compas_geometry)
        vpype_lines.append(shapely_line)
    return vpype_lines


def save_svg(axonometry: Axonometry, filepath: str) -> None:
    """Save the drawing to an SVG file."""
    doc = axonometry.drawing.document
    # use vpype to save file
    write_svg(output=filepath, document=doc, center=True)


def save_json(axonometry: Axonometry, filepath: str) -> None:
    """Dump the scene data to a json file."""
    scene = axonometry.drawing.scene
    scene.to_json(filepath, pretty=False)


def visualize(axonometry: Axonometry) -> None:
    """Not Implemented."""
    raise NotImplementedError


def show_paths(axonometry: Axonometry) -> None:
    """Show the drawing paths with the vpype viewer."""
    # move geometry into center of page
    # TODO: this breaks the use of drawing.extend !
    # prevents from calling the function while script is executed.
    command = (
        config_manager.config["layers"]["axo_system"]["vp_cli"]
        + " "
        + config_manager.config["layers"]["projection_traces"]["vp_cli"]
        + " "
        + config_manager.config["layers"]["geometry"]["vp_cli"]
    )
    execute(
        f"{command} show",
        document=axonometry.drawing.document,
    )


def pair_projections_lines(obj1: Line, obj2: Line) -> None:
    """Include each other in the projections collection."""
    if obj2.key == "xyz":
        obj1.projections["xyz"].append(obj2)
    else:
        obj1.projections[obj2.key] = obj2
    if obj1.key == "xyz":
        obj2.projections["xyz"].append(obj1)
    else:
        obj2.projections[obj1.key] = obj1

    pair_projections_points(obj1.start, obj2.start)
    pair_projections_points(obj1.end, obj2.end)


def pair_projections_points(obj1: Point, obj2: Point) -> None:
    """Include each other in the projections collection."""
    if obj2.key == "xyz":
        obj1.projections["xyz"].append(obj2)
    else:
        obj1.projections[obj2.key] = obj2
    if obj1.key == "xyz":
        obj2.projections["xyz"].append(obj1)
    else:
        obj2.projections[obj1.key] = obj1


def random_axo_ref_plane_keys(
    *,
    force_plane: str | None = None,
    privilege_xy_plane: bool = True,
) -> list[Literal["xy", "yz", "zx"]]:
    """Compute XY and second random key."""
    all_planes = ["xy", "yz", "zx"]
    random_planes = []
    if force_plane:
        random_planes.append(force_plane)
        all_planes.remove(force_plane)
        random_planes.append(random.choice(all_planes))  # noqa: S311
    elif privilege_xy_plane:
        random_planes = ["xy", random.choice(["yz", "zx"])]  # noqa: S311
    else:
        random_planes = list(random.sample(all_planes, 2))

    return random_planes


def random_valid_angles() -> tuple:
    """Compute an angle pair which can produce a valid axonometric drawing.

    The notation follows standard hand-drawn axonometry conventions expressed as a tuple of
    the two angles between the X and Y from the "axonoemtric horizon".

    TODO: allow a zero angle value.

    """
    alpha = random.choice(list(range(91)))  # noqa: S311
    beta = random.choice(list(range(91)))  # noqa: S311
    while not is_valid_angles((alpha, beta)):
        alpha = random.choice(list(range(91)))  # noqa: S311
        beta = random.choice(list(range(91)))  # noqa: S311

    return (alpha, beta)


def is_valid_angles(angles: tuple) -> bool:
    """Test if an angle pair are valid axonometry angles.

    Check if angles satisfy the following conditions::

        not (180 - (alpha + beta) >= 90 and
        not (alpha == 0 and beta == 0) and
        not (alpha == 90 and beta == 0) and
        not (alpha == 0 and beta == 90)

    .. hint::

        Currently the angle value 0 is not supported.
        But one can use a float vlue of .1 to approximate zero.
    """
    RIGHT_ANGLE = 90
    return (
        180 - (angles[0] + angles[1]) >= RIGHT_ANGLE
        and not (angles[0] == 0 and angles[1] == 0)
        and not (angles[0] == RIGHT_ANGLE and angles[1] == 0)
        and not (angles[0] == 0 and angles[1] == RIGHT_ANGLE)
    )
