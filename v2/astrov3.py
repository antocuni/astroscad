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

class TopPlate(CustomObject):

    def init_custom(self, turntable):
        self.body = Cylinder(d=turntable.d2-1, h=5).mod('%')
        self.sub(holes = FourHoles(turntable.ihd, d=M5))
        self -= Cylinder(d=PH_38, h=6)
        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)


class SpurPlate(CustomObject):

    def init_custom(self, turntable):
        self.body = Cylinder(d=turntable.d2-1, h=2).color('pink')
        spur = WormFactory.spur(teeth=70, h=17, optimized=False,
                                fast_rendering=FAST_RENDERING)
        self.spur = spur.move_to(top=self.body.bottom).color('pink')
        self.sub(holes = FourHoles(turntable.ihd, d=M5))

        # make a big hole to optimize the material
        self -= Cylinder(d=60, h=100)

        # insert some spokes
        spokes = []
        n = 3
        for i in range(n):
            angle = i * (180/n)
            spoke = Cube(2, spur.teeth, 4).rot(z=angle).color('pink')
            spokes.append(spoke)
        self.spokes = spokes

        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)


class BottomPlate(CustomObject):

    PILLAR_H = 30
    BODY_H = 4

    def init_custom(self, turntable):
        self.d = turntable.d4+2
        body = Cylinder(d=self.d, h=self.BODY_H).color('PaleGreen')
        self.body = body

        pillars = []
        for i in range(3):
            a = i*90
            pil = DonutSlice(d1=turntable.d3+2, d2=turntable.d4,
                             h=self.PILLAR_H,
                             start_angle=a-7.5, end_angle=a+7.5)
            pil.move_to(bottom=body.top).color('PaleGreen')
            pillars.append(pil)
        self.pillars = pillars

        self.sub(holes = FourHoles(turntable.ohd, d=M5))

        # motor bracket plate
        mb_plate = Cube(80, 80, self.BODY_H).color('PaleGreen')
        self.mb_plate = mb_plate.move_to(center=body.center,
                                         back=body.front + 40)

        self.anchors.set_bounding_box(body.pmin, body.pmax,
                                      pillars[0].pmin, pillars[0].pmax,
                                      mb_plate.pmin, mb_plate.pmax)


class WormShaft(CustomObject):
    # total length of the Shaft, "bearing to bearing" (including the washers)
    LENGTH = 66
    color = 'LawnGreen'

    WASHER_ID = 4.20
    WASHER_OD = 8.88
    WASHER_H = 0.84

    PLACEHOLDER_SIDE = 5 # section of the square placeholder
    SPUR_TEETH = 18

    def init_custom(self, *, axis):
        lwasher = self.washers(n=2) # left washers
        rwasher = self.washers(n=1) # right washers
        #
        h_spur = 4
        h_worm = 25 + 0.2
        # this is just a worm placeholder
        side = self.PLACEHOLDER_SIDE
        self.worm = worm = Cube(h_worm, side, side).color(self.color)
        #
        # left trunk length, right truck length
        ltl = self.LENGTH/2 - h_worm/2 - h_spur - lwasher.h
        rtl = self.LENGTH/2 - h_worm/2 - rwasher.h
        l_trunk = Cylinder(d=8, h=ltl, axis=axis).color(self.color)
        r_trunk = Cylinder(d=8, h=rtl, axis=axis).color(self.color)
        self.l_trunk = l_trunk.move_to(right=worm.left)
        self.r_trunk = r_trunk.move_to(left=worm.right)
        #
        spur = WormFactory.spur(teeth=self.SPUR_TEETH, h=h_spur, axis=axis,
                                optimized=False,
                                fast_rendering=FAST_RENDERING)
        spur = spur.move_to(center=worm.center, right=l_trunk.left)
        self.spur = spur.color(self.color)
        #
        # central bore
        self -= Cylinder(d=4.2, h=100, axis=axis).move_to(center=worm.center)
        #
        # washers
        lwasher.move_to(center=worm.center, right=spur.left)
        rwasher.move_to(center=worm.center, left=r_trunk.right)

        self.anchors.set_bounding_box(spur.pmin, spur.pmax,
                                      worm.pmin, worm.pmax,
                                      r_trunk.pmin, r_trunk.pmax)
        self.anchors.worm_center = worm.center
        self.anchors.worm_back = worm.back
        #
        # sanity check
        actual_length = rwasher.right.x - lwasher.left.x
        check_almost_equal('WormShaft.LENGTH', self.LENGTH, actual_length)

        # this hole is needed in conjunction with a 3d-printed cylindric axis:
        # if we drill a hole inside the inner axis and fix it with a stick, we
        # can attach the axis to a drill and rotate the worm very fast, useful
        # for running in the system.
        self -= Cylinder(d=2, h=10, axis='y').tr(25, 0, 0) #.mod()

        if VITAMINS:
            self.lwasher = lwasher
            self.rwasher = rwasher


    def washers(self, *, n):
        # we simulate n washers by creating a single thicker washer
        return Washer(d1=self.WASHER_ID, d2=self.WASHER_OD,
                      h=self.WASHER_H*n, axis='x', color='white')




def build():
    global FAST_RENDERING, VITAMINS
    FAST_RENDERING = astro.FAST_RENDERING
    VITAMINS = astro.VITAMINS
    obj = CustomObject()

    turntable = Turntable()
    top_plate = TopPlate(turntable)
    spur_plate = SpurPlate(turntable)
    bottom_plate = BottomPlate(turntable)

    obj.turntable = turntable
    obj.top_plate = top_plate.move_to(bottom=turntable.top)
    obj.spur_plate = spur_plate.move_to(top=turntable.bottom)
    obj.bottom_plate = bottom_plate.move_to(top=turntable.bottom)

    worm = WormFactory.worm(h=25, bore_d=0, axis='x', fast_rendering=FAST_RENDERING)
    worm.mod('%')
    obj.worm = worm.move_to(bottom=spur_plate.spur.bottom, back=spur_plate.spur.front)
    if worm.top.z >= turntable.bottom.z:
        print('WARNING, the worm touches the turntable!')
    if worm.top.z >= spur_plate.body.bottom.z:
        print('WARNING, the worm touches the spur plate')

    worm_shaft = WormShaft(axis='x').move_to(worm_center=worm.center)
    obj.worm_shaft = worm_shaft
    if worm_shaft.spur.top.z >= spur_plate.body.bottom.z:
        print('WARNING, the worm_shaft.spur touches the spur plate')


    return obj


if __name__ == '__main__':
    main(build)
