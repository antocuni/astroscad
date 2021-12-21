#!/usr/bin/python3

import math
import os
from pyscad import (Cube, Cylinder, Sphere, bolt_hole, Point, Union, CustomObject, EPS,
                    TCone)
from pyscad.shapes import DonutSlice
from pyscad.lib.misc import TeflonGlide
from pyscad.lib.bearing import Bearing
from pyscad.lib.gears import WormFactory
from pyscad.lib.photo import Manfrotto_200PL
from pyscad.util import in2mm
from pyscad import autorender

VITAMINS = True

IRON = [0.36, 0.33, 0.33]
BRASS = [0.88, 0.78, 0.5]



class BallHead(CustomObject):

    def init_custom(self):
        self.cyl = Cylinder(d=55, h=30)
        self.ball = Sphere(d=self.cyl.d-10).move_to(center=self.cyl.top)
        self.color([0.4, 0.4, 0.4])
        self.anchors.set_bounding_box(self.cyl.pmin, self.cyl.pmax,
                                      self.ball.pmin, self.ball.pmax)


class PHBolt(CustomObject):
    D = in2mm(1/4)
    TOTAL_H = 50  # mm
    HEAD_H = 3.85 # mm
    H = TOTAL_H + HEAD_H

    def init_custom(self):
        self.head = TCone(d1=14, d2=self.D, h=self.HEAD_H)
        self.thread = Cylinder(d=self.D, h=self.H).move_to(bottom=self.head.top)
        self.anchors.set_bounding_box(self.head.pmin, self.head.pmax,
                                      self.thread.pmin, self.thread.pmax)
        self.color(BRASS)

class BearingBoltAdapter(CustomObject):

    WASHER_H = 1.5
    WASHER_D = 17
    WASHER_INNER_D = 8
    HEAD_H = 3.85

    def init_custom(self, bearing, bolt):
        head = Cylinder(d=self.WASHER_D, h=self.HEAD_H)
        head -= TCone(d1=14, d2=bolt.D, h=self.HEAD_H+EPS*2)
        self.head = head
        self.cyl = DonutSlice(d1=bolt.D,
                              d2=bearing.hole_d,
                              h=bearing.h + self.WASHER_H).move_to(bottom=head.top)

        self.color('white')
        self.anchors.set_bounding_box(self.head.pmin, self.head.pmax,
                                      self.cyl.pmin, self.cyl.pmax)

        if VITAMINS:
            washer = DonutSlice(d1=self.WASHER_INNER_D, d2=self.WASHER_D,
                                h=self.WASHER_H).color('grey')
            self.washer = washer.move_to(bottom=self.head.top)




class BasePlate(CustomObject):

    BEARING_RIM = 5

    def init_custom(self):
        bearing = Bearing('608')
        photo_plate = Manfrotto_200PL(with_holes=True)

        # the smaller d must be large enough to cover the whole photo plate,
        # the larger d must be large enough to cover the spur
        pp_dim = photo_plate.pmax - photo_plate.pmin
        self.d1 = math.hypot(pp_dim.x, pp_dim.y)
        self.d2 = 80

        # the cone must contain the bearing, plus an upper rim which prevents
        # the bearing from "falling up"
        h = bearing.h + self.BEARING_RIM

        self.body = TCone(d1=self.d1, d2=self.d2, h=h).color('SandyBrown')

        # big hole where to put the bearing. h=100 means "very long"
        self -= bearing.hole(h=100)\
            .move_to(top=self.body.top - self.BEARING_RIM)

        # smaller hole to make the bearing accessible from the top
        self -= Cylinder(d=bearing.d-5, h=100)
        if VITAMINS:
            self.bearing = bearing.move_to(bottom=self.body.bottom)
            # XXX re-enable this
            #self.photo_plate = photo_plate.move_to(top=self.body.bottom-EPS)\
            #    .color(IRON, 0.7)


def main():
    obj = CustomObject()
    obj.baseplate = BasePlate()
    obj.spur = WormFactory.spur(teeth=70, h=4, optimized=False)\
                          .move_to(bottom=obj.baseplate.body.top+5)
    obj.worm = WormFactory.worm(length=15, bore_d=4)\
                          .move_to(center=obj.spur.center, left=obj.spur.right)

    bolt = PHBolt()
    adapter = BearingBoltAdapter(obj.baseplate.bearing, bolt)
    obj.adapter = adapter.move_to(top=obj.baseplate.bearing.top)
    obj.bolt = bolt.move_to(bottom=adapter.bottom)

    if VITAMINS:
        obj.ball_head = BallHead().move_to(bottom=obj.baseplate.body.top + 20)

    return obj

if __name__ == '__main__':
    main().autorender()
