#!/usr/bin/python3

import os
from pyscad import (Cube, Cylinder, Sphere, bolt_hole, Point, Union, CustomObject, EPS,
                    TCone)
from pyscad.lib.misc import TeflonGlide
from pyscad.lib.bearing import Bearing
from pyscad.lib.gears import WormFactory
from pyscad import autorender

VITAMINS = True

class BallHead(CustomObject):

    def init_custom(self):
        self.cyl = Cylinder(d=55, h=30)
        self.ball = Sphere(d=self.cyl.d-10).move_to(center=self.cyl.top)
        self.color([0.4, 0.4, 0.4])
        self.anchors.set_bounding_box(self.cyl.pmin, self.cyl.pmax,
                                      self.ball.pmin, self.ball.pmax)


class BasePlate(CustomObject):

    BEARING_RIM = 5

    def init_custom(self):
        bearing = Bearing('608')
        self.d = 80
        self.h = bearing.h + self.BEARING_RIM
        self.base = TCone(d1=bearing.d+5, d2=self.d, h=self.h).color('SandyBrown')
        self -= bearing.hole(h=self.h+EPS)\
            .move_to(top=self.base.top - self.BEARING_RIM)
        self -= Cylinder(d=bearing.d-5, h=self.h+EPS)
        if VITAMINS:
            self.bearing = bearing.move_to(bottom=self.base.bottom)
        self.anchors.copy_from(self.base.anchors)

def main():
    obj = CustomObject()
    obj.baseplate = BasePlate()
    obj.spur = WormFactory.spur(teeth=70, h=4, optimized=False).move_to(bottom=obj.baseplate.top+5)
    obj.worm = WormFactory.worm(length=15, bore_d=4)\
                          .move_to(center=obj.spur.center, left=obj.spur.right)

    if VITAMINS:
        obj.ball_head = BallHead().move_to(bottom=obj.baseplate.top + 20)
    return obj

if __name__ == '__main__':
    main().autorender()
