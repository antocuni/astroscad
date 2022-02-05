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
import astro
from astro import main, check_almost_equal

M5 = 5.5 # diameter of holes for M5 screws
PH_38 = in2mm(3/8) + 0.5  # diameter for holes of 3/8" screws

class FourHoles(CustomObject):

    def init_custom(self, dist, *, d, h=100, angle=0):
        holes = []
        points = []
        for i in range(4):
            a = math.radians(angle + i*90)
            x = dist * math.cos(a)
            y = dist * math.sin(a)
            p = Point(x, y, 0)
            hole = Cylinder(d=d, h=h).move_to(center=p)
            holes.append(hole)
            points.append(p)
        self.holes = holes
        self.points = points


class Turntable(CustomObject):

    def init_custom(self):
        self.d1 = d1 = 70
        self.d2 = d2 = 93.4
        self.d3 = d3 = 95.4
        self.d4 = d4 = 120
        self.h = h = 8.5
        self.ihd = 82/2     # Inner Hole distance
        self.ohd = 107.5/2    # Outer Hole distance
        #
        self.outer = DonutSlice(d1=d1, d2=d2, h=h).color('grey')
        self.inner = DonutSlice(d1=d3, d2=d4, h=h).color('grey')
        self.sub(inner_holes = FourHoles(self.ihd, d=5))
        self.sub(outer_holes = FourHoles(self.ohd, d=5))
        self.anchors.set_bounding_box(self.outer.pmin, self.outer.pmax)

class UpperPlate(CustomObject):

    def init_custom(self, turntable):
        self.body = Cylinder(d=turntable.d2-1, h=5).mod('%')
        self.sub(holes = FourHoles(turntable.ihd, d=M5))
        self -= Cylinder(d=PH_38, h=6)
        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)


class SpurPlate(CustomObject):

    def init_custom(self, turntable):
        self.body = Cylinder(d=turntable.d2-1, h=2).color('pink')
        spur = WormFactory.spur(teeth=70, h=13, optimized=True,
                                fast_rendering=FAST_RENDERING)
        self.spur = spur.move_to(top=self.body.bottom).color('pink')
        self.sub(holes = FourHoles(turntable.ihd, d=M5))
        self -= Cylinder(d=18, h=100)
        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)


class BottomBase(CustomObject):

    PILLAR_H = 30
    BASE_H = 4

    def init_custom(self, turntable):
        self.d = turntable.d4+2
        base = Cylinder(d=self.d, h=self.BASE_H).color('PaleGreen')
        self.base = base

        pillars = []
        for i in range(3):
            a = i*90
            pil = DonutSlice(d1=turntable.d3+2, d2=turntable.d4,
                             h=self.PILLAR_H,
                             start_angle=a-7.5, end_angle=a+7.5)
            pil.move_to(bottom=base.top).color('PaleGreen')
            pillars.append(pil)
        self.pillars = pillars

        self.sub(holes = FourHoles(turntable.ohd, d=M5))

        base2 = Cube(80, 80, self.BASE_H).color('PaleGreen')
        self.base2 = base2.move_to(center=base.center,
                                   back=base.front + 40)

        self.anchors.set_bounding_box(base.pmin, base.pmax,
                                      pillars[0].pmin, pillars[0].pmax)




def build():
    global FAST_RENDERING, VITAMINS
    FAST_RENDERING = astro.FAST_RENDERING
    VITAMINS = astro.VITAMINS
    obj = CustomObject()

    turntable = Turntable()
    upper_plate = UpperPlate(turntable)
    spur_plate = SpurPlate(turntable)
    bottom_base = BottomBase(turntable)

    obj.turntable = turntable
    obj.upper_plate = upper_plate.move_to(bottom=turntable.top)
    obj.spur_plate = spur_plate.move_to(top=turntable.bottom)
    obj.bottom_base = bottom_base.move_to(top=turntable.bottom)

    worm = WormFactory.worm(h=20, bore_d=0, axis='x', fast_rendering=FAST_RENDERING)
    worm.mod('%')
    obj.worm = worm.move_to(bottom=spur_plate.spur.bottom, back=spur_plate.spur.front)
    if worm.top.z >= turntable.bottom.z:
        print('WARNING, the worm touches the turntable!')
    if worm.top.z >= spur_plate.body.bottom.z:
        print('WARNING, the worm touches the spur plate')

    return obj


if __name__ == '__main__':
    main(build)
