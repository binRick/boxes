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


class WoodHinge(Boxes):
    """Flat-pack butt hinge: two slotted leaves joined by a loose barrel and pin

Two hinge leaves are joined by a set of barrel rings that thread through
alternating knuckle mortises on each leaf's pivot edge. A pin rod locks the
rings together. The assembly can rotate freely around the pin axis. Cut all
parts from the same sheet; the number of rings equals (2 * knuckles - 1).
"""

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.argparser.add_argument(
            "--hinges", action="store", type=int, default=2,
            help="number of complete hinges to generate")
        self.argparser.add_argument(
            "--leaf_width", action="store", type=float, default=56.0,
            help="length of each leaf along the pivot axis (mm)")
        self.argparser.add_argument(
            "--leaf_depth", action="store", type=float, default=22.0,
            help="depth of each leaf away from the pivot edge (mm)")
        self.argparser.add_argument(
            "--knuckles", action="store", type=int, default=3,
            help="knuckle slots in the primary leaf (secondary gets knuckles-1); "
                 "total barrel rings = 2*knuckles-1")
        self.argparser.add_argument(
            "--knuckle_depth", action="store", type=float, default=0.0,
            help="how deep the knuckle mortises cut into the leaf from the pivot "
                 "edge (mm); 0 = auto: barrel_diameter/2 leaving ring centre "
                 "flush with the edge")
        self.argparser.add_argument(
            "--barrel_diameter", action="store", type=float, default=17.0,
            help="outer diameter of the barrel rings (mm)")
        self.argparser.add_argument(
            "--pin_diameter", action="store", type=float, default=5.0,
            help="diameter of the central pin hole through the barrel rings (mm)")
        self.argparser.add_argument(
            "--screw_diameter", action="store", type=float, default=4.0,
            help="diameter of the mounting screw holes on each leaf (mm)")
        self.argparser.add_argument(
            "--screw_margin", action="store", type=float, default=8.0,
            help="distance from screw hole centres to the nearest leaf edges (mm)")

    # ------------------------------------------------------------------ parts

    def hinge_leaf(self, knuckle_count, slot_offset, move=None, label="leaf"):
        """Draw one hinge leaf.

        knuckle_count: number of mortises on this leaf.
        slot_offset: 0 for the primary leaf (mortises at even positions),
                     1 for the secondary leaf (mortises at odd positions).
        """
        w = self.leaf_width
        d = self.leaf_depth
        t = self.thickness
        slot_w = t + 0.1       # slot accepts one ring thickness
        slot_h = self._slot_h  # depth of the mortise from the pivot edge
        total = 2 * self.knuckles - 1
        step = w / total       # pitch per knuckle

        def cb():
            # Screw holes at the four quadrants of the mounting face
            sm = self.screw_margin
            sr = self.screw_diameter / 2
            self.hole(sm,     d - sm, sr)
            self.hole(w - sm, d - sm, sr)

            # Knuckle mortises along the pivot edge (y = 0)
            for i in range(knuckle_count):
                cx = step * (slot_offset + 2 * i) + step / 2
                # rectangularHole(x, y, dx, dy) — (x,y) is the centre
                self.rectangularHole(cx, slot_h / 2, slot_w, slot_h)

        self.rectangularWall(w, d, "eeee", callback=[cb],
                             move=move, label=label)

    def barrel_ring(self, move=None):
        """Draw one barrel ring (annular disc)."""
        r = self.barrel_diameter / 2
        ri = self.pin_diameter / 2
        tw = th = 2 * r

        if self.move(tw, th, move, True):
            return

        # Pin hole (inner cut)
        self.hole(r, r, ri)

        # Outer contour: full circle, radius r, centre at (r, r).
        # Start at the left-middle point (0, r) heading up; a -360° (clockwise)
        # arc with radius r has its centre r units to the right of the heading,
        # which is (0, r) + (r, 0) = (r, r). ✓
        self.moveTo(0, r, 90)
        self.corner(-360, r)

        self.move(tw, th, move)

    def pin_bar(self, move=None):
        """Draw the pivot pin bar that locks the barrel rings together."""
        total = 2 * self.knuckles - 1
        # Pin must span the full stack of rings plus a small margin at each end
        length = total * (self.thickness + 0.1) + 2.0
        # Slight undersize so it slides through the ring holes
        width = self.pin_diameter - 0.2
        self.rectangularWall(width, length, "eeee",
                             move=move, label="pin")

    # ------------------------------------------------------------------ render

    def render(self):
        t = self.thickness
        total = 2 * self.knuckles - 1  # total barrel rings

        # Resolve auto knuckle_depth
        self._slot_h = (self.knuckle_depth if self.knuckle_depth > 0
                        else self.barrel_diameter / 2)

        # Validate
        if self.knuckles < 2:
            raise ValueError("knuckles must be at least 2")
        if self.barrel_diameter <= 2 * self.pin_diameter:
            raise ValueError("barrel_diameter must be more than 2 × pin_diameter")
        if self._slot_h >= self.leaf_depth - self.screw_margin - self.screw_diameter:
            raise ValueError(
                "leaf_depth too small for knuckle_depth + screw_margin + screw_diameter")
        if self.screw_margin + self.screw_diameter / 2 >= self.leaf_width / 2:
            raise ValueError(
                "screw_margin too large for leaf_width")

        for _ in range(self.hinges):
            self.hinge_leaf(
                self.knuckles, 0, move="up",
                label=f"leaf A ({self.knuckles} knuckles)")
            self.hinge_leaf(
                self.knuckles - 1, 1, move="up",
                label=f"leaf B ({self.knuckles - 1} knuckles)")
            for _ in range(total):
                self.barrel_ring(move="up")
            self.pin_bar(move="up")
