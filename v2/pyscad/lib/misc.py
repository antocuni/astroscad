from ..geometry import Point
from ..scad import Cylinder, EPS, CustomObject
from ..shapes import DonutSlice
from ..calibration import CalibrationData

def ring(outer_d, inner_d, h, *, axis='z'):
    result = Cylinder(d=outer_d, h=h, axis=axis)
    result -= Cylinder(d=inner_d, h=h+EPS, axis=axis)
    return result


class TeflonGlide(CustomObject):
    # https://www.amazon.com/dp/B07FH82D8J
    # measures took manually

    def init_custom(self):
        self.d = 19
        self.inner_d = 9.20
        self.hole_d = 4.30
        self.base_h = 3.5
        self.upper_h = 1.9
        self.h = self.base_h + self.upper_h
        self._teflon = ring(self.d, self.inner_d, self.upper_h)\
            .move_to(bottom=Point.O)\
            .color('LightSteelBlue')
        self._base = ring(self.d, self.hole_d, self.base_h)\
            .color([0.3, 0.3, 0.3])\
            .move_to(bottom=self._teflon.top)
        #
        self.translate(z = -self.h/2)
        self.anchors.set_bounding_box(self._teflon.pmin, self._base.pmax)
        self.anchors.center = Point.O

    def make_groove(self, h):
        clearance = CalibrationData.TEFLON_GLIDE_GROOVE_CLEARANCE
        return Cylinder(d=self.d + clearance, h=h).move_to(center=self.center)


class RoundHole(CustomObject):
    """
    Like a Cylinder, but it is meant to be used as a negative part to make a hole.

    It supports adding extra reinforcing walls by using the technique
    described here:
    https://3dprinting.stackexchange.com/questions/7019/using-multiple-infill-types-within-one-model/7022#7022

    NOTE: it is hard to automatically test that it "works", i.e. that Cura
    creates extra walls after slicing. The default params seem to work with my
    current settings, but before printing it is adviced to double check that
    it works as intended:
      1. run TestRoundHole.test_negative
      2. open /tmp/pytest.scad in Cura
      3. slice
      4. manually check that it contains multiple walls around the hole, with
         no visible gap in between
    """

    # this must match the "Wall Thickness" setting in cura, and it's used to
    # determine where to cut the thin ring
    _WALL_THICKNESS = 1.6

    # size of the ring: it creates a very small gap which will be filled by
    # plastic anyway, but that convinces Cura to create the extra walls
    _GAP = 0.02

    def init_custom(self, *, extra_walls=0, **kwargs):
        self.hole = Cylinder(**kwargs)
        # we explicitly do NOT consider the extra rings as part of the
        # bounding box. They exists solely for the sake of the slicer, but
        # they should not have any other structural behavior
        self.anchors.set_bounding_box(self.hole.pmin, self.hole.pmax)
        for i in range(extra_walls):
            self._add_ring(i)

    def _add_ring(self, i):
        W = self._WALL_THICKNESS
        G = self._GAP
        r = self.hole.r
        h = self.hole.h
        axis = self.hole.axis
        #
        x = r + (W+G)*(i+1)
        ring = Cylinder(r=x, h=h, axis=axis) - Cylinder(r=x-G, h=h+EPS, axis=axis)
        self += ring


def Washer(*, d1, d2, h, color='grey'):
    assert d1 < d2
    return DonutSlice(d1=d1, d2=d2, h=h).color(color)
