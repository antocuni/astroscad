#!./venv/bin/python3

import math
from pyscad import (Cube, Cylinder, Sphere, Point, Union, CustomObject, EPS,
                    TCone, Vector, PySCADObject)
from pyscad.shapes import DonutSlice
from pyscad.lib.misc import RoundHole, Washer
from pyscad.lib.bearing import Bearing
from pyscad.lib.gears import WormFactory
from pyscad.lib.photo import Manfrotto_200PL
from pyscad.lib.motors import Stepper_28BYJ48
from pyscad.util import in2mm
from astro import main, check_almost_equal

class FourHoles(CustomObject):

    def init_custom(self, dist, *, d, h=10):
        r = dist
        self.h1 = h1 = Cylinder(d=d, h=h).move_to(center=Point( r, 0, 0))
        self.h2 = h2 = Cylinder(d=d, h=h).move_to(center=Point(-r, 0, 0))
        self.h3 = h3 = Cylinder(d=d, h=h).move_to(center=Point(0,  r, 0))
        self.h4 = h4 = Cylinder(d=d, h=h).move_to(center=Point(0, -r, 0))
        self.anchors.set_bounding_box(h1.pmin, h1.pmax,
                                      h2.pmin, h2.pmax,
                                      h3.pmin, h3.pmax,
                                      h4.pmin, h4.pmax)

class RotatingPlate(CustomObject):

    def init_custom(self):
        self.d1 = d1 = 70
        self.d2 = d2 = 93.4
        self.d3 = d3 = 95.4
        self.d4 = d4 = 120
        self.h = h = 8.6
        self.ihd = 82/2     # Inner Hole distance
        self.ohd = 107.5/2    # Outer Hole distance
        #
        self.outer = DonutSlice(d1=d1, d2=d2, h=h).color('grey')
        self.inner = DonutSlice(d1=d3, d2=d4, h=h).color('grey')
        self.sub(inner_holes = FourHoles(self.ihd, d=5))
        self.sub(outer_holes = FourHoles(self.ohd, d=5))


def build():
    obj = CustomObject()
    obj.rplate = RotatingPlate()
    return obj


if __name__ == '__main__':
    main(build)
