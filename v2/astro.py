#!/usr/bin/python3

import os
from pyscad import Cube, Cylinder, Sphere, bolt_hole, Point, Union, CustomObject, EPS
from pyscad.lib.misc import TeflonGlide
from pyscad.lib.bearing import Bearing
from pyscad import autorender

class BasePlate(CustomObject):

    BEARING_RIM = 5

    def init_custom(self):
        bearing = Bearing('608')
        self.d = 100
        self.h = bearing.h + self.BEARING_RIM
        self.base = Cylinder(d=self.d, h=self.h).color('SandyBrown')
        self -= bearing.hole(h=self.h+EPS)\
            .move_to(top=self.base.top - self.BEARING_RIM)
        self -= Cylinder(d=14, h=self.h+EPS)
        self.bearing = bearing.move_to(bottom=self.base.bottom)

def main():
    obj = CustomObject()
    obj.baseplate = BasePlate()
    return obj

if __name__ == '__main__':
    main().autorender()
