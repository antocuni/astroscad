import solid
from .scad import PySCADObject, _get_r_d
from .geometry import Point, Vector, AnchorPoints

_shapes2d = solid.import_scad('MCAD/2Dshapes.scad')

class DonutSlice(PySCADObject):

    def init_solid(self, *, h, r1=None, r2=None, d1=None, d2=None,
                   start_angle=0, end_angle=360):
        self.r1, self.d1 = _get_r_d(r1, d1)
        self.r2, self.d2 = _get_r_d(r2, d2)
        self.h = h
        self.start_angle = start_angle
        self.end_angle = end_angle
        donut = _shapes2d.donutSlice(self.r1, self.r2, start_angle, end_angle)
        self.solid = solid.translate([0, 0, -h/2])(
            solid.linear_extrude(h)(
                donut
            )
        )
        r2 = self.r2
        pmin = Point(-r2, -r2, -h/2)
        pmax = Point(r2, r2, h/2)
        self.anchors.set_bounding_box(pmin, pmax)
        self.anchors.center = Point.O
