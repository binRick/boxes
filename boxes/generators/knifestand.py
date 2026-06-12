# Copyright (C) 2026 Richard Blundell
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *


class KnifeStand(Boxes):
    """Tiered display stand for knives with scalloped cradles"""

    description = """Knives rest sideways in pairs of scalloped cradles cut
into the sloped front edges of the two side panels, blades lying flat on the
shelf behind each cradle. Handles stick out to the front. Each shelf sits
flush with the resting point of its cradle and braces the two sides together.
"""

    ui_group = "Shelf"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.argparser.add_argument(
            "--knives", action="store", type=int, default=5,
            help="number of knives")
        self.argparser.add_argument(
            "--width", action="store", type=float, default=150.0,
            help="inner width between the side panels")
        self.argparser.add_argument(
            "--height", action="store", type=float, default=330.0,
            help="total height of the side panels")
        self.argparser.add_argument(
            "--depth", action="store", type=float, default=240.0,
            help="total depth of the side panels")
        self.argparser.add_argument(
            "--cradle_diameter", action="store", type=float, default=35.0,
            help="diameter of the knife cradles")
        self.argparser.add_argument(
            "--shelf_depth", action="store", type=float, default=45.0,
            help="depth of the shelves behind the cradles")
        self.argparser.add_argument(
            "--top_depth", action="store", type=float, default=45.0,
            help="depth of the flat area on top, behind the topmost cradle")
        self.argparser.add_argument(
            "--base_height", action="store", type=float, default=40.0,
            help="height of the front edge below the lowest cradle")

    def cradlePositions(self):
        """Center of each cradle on the front edge, top tier first."""
        for i in range(self.knives):
            s = (i + 0.5) * self.tier
            yield (self.depth - self.top_depth - s * self.dx / self.diag,
                   self.height - s * self.dy / self.diag)

    def shelfHoleAt(self, cx, cy):
        """Start point and height of the shelf finger holes for a cradle."""
        r1, r2 = self.r1, self.r2
        # resting point: lowest point of the cradle arc's circle
        bowl = (r1 + r2) * (1 - math.cos(math.radians(self.cradle_angle)))
        ox = cx + (bowl - r1) * self.dy / self.diag
        oy = cy - (bowl - r1) * self.dx / self.diag
        py = oy - r1 - 0.5 * self.thickness
        # keep at least 2*t of material between the holes and the cradle arc
        web = max(r1 ** 2 - (r1 - 2 * self.thickness) ** 2, 0)
        return ox + math.sqrt(web) + 1, py

    def side(self, move=None):
        t = self.thickness
        tw, th = self.depth, self.height

        if self.move(tw, th, move, True):
            return

        for cx, cy in self.cradlePositions():
            px, py = self.shelfHoleAt(cx, cy)
            self.fingerHolesAt(px, py, self.shelf_depth, 0)

        a, r1, r2 = self.cradle_angle, self.r1, self.r2
        nose = (self.tier - self.extent) / 2
        # polyline arguments strictly alternate edge, corner, edge, ...
        front = [nose]
        for i in range(self.knives):
            front += [(a, r2), 0, (-2 * a, r1), 0, (a, r2),
                      2 * nose if i < self.knives - 1 else nose]
        gamma = math.degrees(math.atan2(self.dy, self.dx))
        self.polyline(
            self.depth, 90, self.height, 90, self.top_depth, gamma,
            *front,
            90 - gamma, self.base_height, 90)

        self.move(tw, th, move, label="side")

    def render(self):
        t = self.thickness
        self.cradle_angle = 60
        self.r1 = self.cradle_diameter / 2
        self.r2 = self.r1 / math.cos(math.radians(90 - self.cradle_angle)) \
            - self.r1
        self.extent = 2 * (self.r1 + self.r2) * \
            math.sin(math.radians(self.cradle_angle))
        self.dx = self.depth - self.top_depth
        self.dy = self.height - self.base_height
        if self.dx <= 10 or self.dy <= 10:
            raise ValueError(
                "depth/height too small for top_depth/base_height")
        self.diag = math.hypot(self.dx, self.dy)
        self.tier = self.diag / self.knives

        if self.tier < self.extent + 6:
            raise ValueError(
                "Cradles don't fit: use fewer knives, smaller "
                "cradle_diameter or a larger stand")
        top_px = self.shelfHoleAt(*next(iter(self.cradlePositions())))[0]
        if top_px + self.shelf_depth > self.depth - 5:
            raise ValueError(
                "shelf_depth too large: top shelf does not fit "
                "inside the side panel")
        bottom = list(self.cradlePositions())[-1]
        if self.shelfHoleAt(*bottom)[1] < 5:
            raise ValueError(
                "base_height too small: lowest shelf does not fit")

        self.side(move="up")
        self.side(move="up")
        for i in range(self.knives):
            self.rectangularWall(
                self.width, self.shelf_depth, "efef",
                move="up", label=f"shelf {i + 1}")
