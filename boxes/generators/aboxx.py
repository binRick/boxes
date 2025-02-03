from boxes import *
from boxes.lids import LidSettings


class ABoxx(Boxes):
    """A simple Box"""

    description = "This box is kept simple on purpose. If you need more features have a look at the UniversalBox."

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(LidSettings)
        self.buildArgParser("x", "y", "h", "outside", "bottom_edge")
        self.argparser.add_argument(
            "--d1", action="store", type=float, default=2.,
            help="Diameter of the inner lid screw holes in mm")
        self.argparser.add_argument(
            "--d2", action="store", type=float, default=2.,
            help="d1")

    def render(self):
        x, y, h = self.x, self.y, self.h
        d1 = self.d1
        t = self.thickness

        t1, t2, t3, t4 = "eeee"
        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F" # if self.vertical_edges == "finger joints" else "h"

        if self.outside:
            self.x = x = self.adjustSize(x, sideedge, sideedge)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h, b, t1)

        with self.saved_context():
            self.rectangularWall(x, h, [b, sideedge, t1, sideedge],
                                 ignore_widths=[1, 6], move="up")
            self.rectangularWall(x, h, [b, sideedge, t3, sideedge],
                                 ignore_widths=[1, 6], move="up")

            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", move="up")
            self.lid(x, y)

        self.rectangularWall(x, h, [b, sideedge, t3, sideedge],
                             ignore_widths=[1, 6], move="right only")
        self.rectangularWall(y, h, [b, "f", t2, "f"],
                             ignore_widths=[1, 6], move="up")
        self.rectangularWall(y, h, [b, "f", t4, "f"],
                             ignore_widths=[1, 6], move="up")
        self.rectangularWall(y, h, [b, "f", t4, "f"],
                             callback=[None, lambda: self.hole(5, 5, d=d1)],
                             ignore_widths=[1, 6], move="up",
			    )
        self.rectangularTriangle(5, 5, "ffe", num=4,
            callback=[None, lambda: self.hole(5, 5, d=d1)])

        print("\nOK2025\n")
