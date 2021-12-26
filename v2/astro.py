#!./venv/bin/python3

import sys
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

    def init_custom(self, bearing, adapter, photo_plate):
        # the smaller d must be large enough to cover the whole photo plate,
        # the larger d must be large enough to cover the spur
        pp_dim = photo_plate.pmax - photo_plate.pmin
        self.d1 = math.hypot(pp_dim.x, pp_dim.y)
        self.d2 = 90

        # the cone must be tall enough to contain:
        #   1. the bearing
        #   2. an upper rim which prevents the bearing from "falling up"
        #   3. the washer
        #   4. the bearing-bolt adapter
        #   5. some additional space to make sure that the bolt does not
        #      hit the photo_plate
        h = (bearing.h +
             self.BEARING_RIM +
             adapter.WASHER_H +
             adapter.HEAD_H +
             2)
        self.body = TCone(d1=self.d1, d2=self.d2, h=h).color('SandyBrown') #.mod('#')
        self.rim_bottom = self.body.top - self.BEARING_RIM

        # big hole where to put the bearing. h=100 means "very long"
        self -= bearing.hole(h=100)\
            .move_to(top=self.body.top - self.BEARING_RIM)

        # smaller hole to make the bearing accessible from the top
        self -= Cylinder(d=bearing.d-5, h=100)


class RotatingPlate(CustomObject):

    GROOVE_H = 1

    def init_custom(self, bolt):
        self.spur = WormFactory.spur(teeth=70, h=4, bore_d=bolt.D+0.1, optimized=False)
        self.anchors.set_bounding_box(self.spur.pmin, self.spur.pmax)
        #
        glides = []
        for angle in (0, 120, 240):
            glide = TeflonGlide()
            r = (self.spur.d - glide.d) / 2 - 5
            angle = math.radians(angle)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            groove = glide.make_groove(self.GROOVE_H + EPS)
            groove.move_to(
                center=Point(x=x, y=y, z=None),
                top=self.spur.bottom + self.GROOVE_H
            )
            self -= groove
            glide.move_to(
                center=groove.center,
                top=groove.top
            )
            glides.append(glide)

        self.glides = glides


def build():
    obj = CustomObject()
    bearing = Bearing('608')
    bolt = PHBolt()
    adapter = BearingBoltAdapter(bearing, bolt)
    photo_plate = Manfrotto_200PL(with_holes=True)

    obj.baseplate = BasePlate(bearing, adapter, photo_plate)
    obj.adapter = adapter.move_to(top=bearing.top)

    if VITAMINS:
        obj.bolt = bolt.move_to(bottom=adapter.bottom)
        obj.bearing = bearing.move_to(top=obj.baseplate.rim_bottom)
        obj.photo_plate = photo_plate.move_to(top=obj.baseplate.body.bottom-EPS)\
                                     .color(IRON, 0.7)


    rplate = RotatingPlate(bolt)
    obj.rplate = rplate.move_to(bottom=obj.baseplate.body.top+25)
    #return rplate

    obj.worm = WormFactory.worm(length=15, bore_d=4)\
                          .move_to(center=rplate.spur.center, left=rplate.spur.right)

    ## if VITAMINS:
    ##     obj.ball_head = BallHead().move_to(bottom=obj.baseplate.body.top + 20)

    return obj

def main():
    part_name = None
    if len(sys.argv) >= 2:
        part_name = sys.argv[1]
    #
    obj = build()
    if part_name:
        obj = getattr(obj, part_name)
    obj.autorender()

if __name__ == '__main__':
    main()
