from ..geometry import Point
from ..scad import Cylinder, EPS, CustomObject

def ring(outer_d, inner_d, h):
    result = Cylinder(d=outer_d, h=h)
    result -= Cylinder(d=inner_d, h=h+EPS)
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
        self._base = ring(self.d, self.hole_d, self.base_h)\
            .color([0.3, 0.3, 0.3])\
            .move_to(bottom=Point.O)
        self._upper = ring(self.d, self.inner_d, self.upper_h)\
            .move_to(bottom=self._base.top-EPS)\
            .color('LightSteelBlue')
        #
        self.translate(z = -self.h/2)
        self.anchors.set_bounding_box(self._base.pmin, self._upper.pmax)
        self.anchors.center = Point.O
