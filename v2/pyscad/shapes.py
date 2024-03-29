import math
import solid
from .scad import PySCADObject, _get_r_d, Cylinder
from .geometry import Point, Vector, AnchorPoints

_shapes2d = solid.import_scad('MCAD/2Dshapes.scad')

class DonutSlice(PySCADObject):

    def init_solid(self, *, h, r1=None, r2=None, d1=None, d2=None,
                   start_angle=0, end_angle=360, axis='z'):
        self.r1, self.d1 = _get_r_d(r1, d1)
        self.r2, self.d2 = _get_r_d(r2, d2)
        self.h = h
        self.start_angle = start_angle
        self.end_angle = end_angle
        donut = _shapes2d.donutSlice(self.r1, self.r2, start_angle, end_angle)
        donut3d = solid.translate([0, 0, -h/2])(
            solid.linear_extrude(h)(
                donut
            )
        )
        # compute the equivalent cylinder
        cyl = Cylinder(d=self.d2, h=h, axis=axis)
        donut3d = solid.rotate(cyl.rot_vector)(donut3d)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        self.solid = donut3d

def CirumscribedHexagon(*, h, axis='z', r=None, d=None):
    """
    Generates a 3d hexagon which circumscribes the cylinder with the given
    radius/diameter.
    In other words, the d is the distance between two SIDES.
    """
    r, d = _get_r_d(r, d)
    ri = r / math.cos(math.radians(30))
    return Cylinder(r=ri, h=h, axis=axis, segments=6)


def HexKey(*, size, h, axis='z'):
    """
    Hex/allen key of the given size (i.e., the side-to-side diameter).
    """
    return CirumscribedHexagon(d=size, h=h, axis=axis)
