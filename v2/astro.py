#!./venv/bin/python3

import sys
import math
import os
from pyscad import (Cube, Cylinder, Sphere, bolt_hole, Point, Union, CustomObject, EPS,
                    TCone)
from pyscad.shapes import DonutSlice
from pyscad.lib.misc import TeflonGlide, RoundHole
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
        self.bcyl = bcyl = Cylinder(d=55, h=8) # base cylinder
        self.cyl = Cylinder(d=45, h=52).move_to(bottom=bcyl.top)
        self.ball = Sphere(d=self.cyl.d-10).move_to(center=self.cyl.top)
        screw_hole = RoundHole(d=in2mm(3/8), h=25)
        self -= screw_hole.move_to(center=bcyl.center, bottom=bcyl.bottom-EPS*2)
        # handles
        h3 = Cylinder(d=22.40, h=18, axis='x')
        h9 = Cylinder(d=22.40, h=18, axis='x')
        h6 = Cylinder(d=19.40, h=18.60, axis='y')
        self.h3 = h3.move_to(center=self.cyl.center, left=self.cyl.right)
        self.h6 = h6.move_to(back=self.cyl.front, bottom=bcyl.bottom+7)
        self.h9 = h9.move_to(center=self.cyl.center, right=self.cyl.left)
        #
        self.color([0.4, 0.4, 0.4])
        self.anchors.set_bounding_box(self.bcyl.pmin, self.bcyl.pmax,
                                      self.cyl.pmin, self.cyl.pmax,
                                      self.ball.pmin, self.ball.pmax)
        self.anchors.screw_hole_top = screw_hole.top


class PHBolt(CustomObject):
    D = in2mm(1/4)
    TOTAL_H = 50  # mm
    HEAD_H = 3.85 # mm
    H = TOTAL_H + HEAD_H

    def init_custom(self):
        self.head = TCone(d1=14, d2=self.D, h=self.HEAD_H)
        self.thread = Cylinder(d=self.D, h=self.H).move_to(bottom=self.head.top)
        self -= Cylinder(d=4.5, h=self.HEAD_H, segments=6).move_to(bottom=self.head.bottom-EPS)
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
        self -= bearing.hole(h=100, extra_walls=1)\
            .move_to(top=self.body.top - self.BEARING_RIM)

        # screw holes to attach the photo plate
        pp = photo_plate
        for p in (pp.hole3, pp.hole6, pp.hole9, pp.hole12):
            screw_hole = RoundHole(d=3, h=18, extra_walls=1)
            self -= screw_hole.move_to(center=p, bottom=self.body.bottom-EPS)

        # smaller hole to make the bearing accessible from the top
        self -= Cylinder(d=bearing.d-5, h=100)


class RotatingPlate(CustomObject):

    GROOVE_H = 1

    def init_custom(self, bolt):
        self.spur = WormFactory.spur(teeth=70, h=4, bore_d=bolt.D+0.1, optimized=False)
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
        self.anchors.set_bounding_box(self.spur.pmin, self.spur.pmax,
                                      self.glides[0].pmin, self.glides[0].pmax)



class SmallWormFactory(WormFactory):
    module = 0.5


class MyWorm(CustomObject):

    def init_custom(self, *, axis):
        self.worm = worm = WormFactory.worm(h=40, bore_d=0, axis=axis)
        spur = SmallWormFactory.spur(teeth=24, h=4, axis=axis, optimized=False)
        self.spur = spur = spur.move_to(center=worm.center, left=worm.right)
        l_bulge = Cylinder(d=8, h=2, axis=axis).color('orange')
        r_bulge = Cylinder(d=8, h=2, axis=axis).color('orange')
        self.l_bulge = l_bulge.move_to(left=spur.right)
        self.r_bulge = r_bulge.move_to(right=worm.left)
        # central bore
        self -= Cylinder(d=3.1, h=100, axis=axis).move_to(center=worm.center)

        self.anchors.set_bounding_box(spur.pmin, spur.pmax,
                                      worm.pmin, worm.pmax,
                                      l_bulge.pmin, l_bulge.pmax,
                                      r_bulge.pmin, r_bulge.pmax)
        self.anchors.worm_center = worm.center
        self.anchors.worm_back = worm.back


class WormBracket(CustomObject):

    B = 1.5 # extra border around the bearings

    def init_custom(self, myworm):
        b = self.B
        lb = Bearing('604', axis='x')    # left bearing
        rb = Bearing('604', axis='x')    # right bearing
        lpil = self.pillar(lb, 'left')   # left pillar
        rpil = self.pillar(rb, 'right')  # right pillar
        #
        self.lpil = lpil.move_to(socket_center=myworm.center, right=myworm.left)
        self.rpil = rpil.move_to(socket_center=myworm.center, left=myworm.right)
        #
        if VITAMINS:
            self.lb = lb.move_to(center=lpil.socket_center, right=lpil.socket_right)
            self.rb = rb.move_to(center=rpil.socket_center, left=rpil.socket_left)

    def pillar(self, bearing, which):
        assert which in ('left', 'right')
        b = self.B
        p = Cube(bearing.h + 4, bearing.d + b*2, 20)
        #
        socket = bearing.hole(bearing.h + 1)
        if which == 'left':
            socket.move_to(top=p.top-b, right=p.right+EPS)
        else:
            socket.move_to(top=p.top-b, left=p.left-EPS)
        p -= socket
        #
        p -= RoundHole(d=9, h=100, axis='x').move_to(center=socket.center)
        p.anchors.socket_center = socket.center
        p.anchors.socket_left = socket.left
        p.anchors.socket_right = socket.right
        return p


def build_worm_bracket():
    obj = CustomObject()
    obj.myworm = MyWorm(axis='x')
    obj.bracket = WormBracket(obj.myworm)
    return obj


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
    obj.rplate = rplate.move_to(bottom=obj.baseplate.body.top) #+25)
    #return rplate

    obj.myworm = MyWorm(axis='x').move_to(worm_center=rplate.spur.center,
                                          worm_back=rplate.spur.front)
    obj.bracket = WormBracket(obj.myworm)

    if VITAMINS:
        ball_head = BallHead().move_to(bottom=obj.rplate.top)
        obj.ball_head = ball_head
        diff = bolt.top.z - ball_head.screw_hole_top.z
        if diff > 0:
            ball_head.mod()
            print(f'** WARNING **: the bolt is too long for the ball head: {diff:.2f}')
            print('baseplate H: ', obj.baseplate.body.top.z - obj.baseplate.body.bottom.z)

    return obj

def main():
    part_name = None
    if len(sys.argv) >= 2:
        part_name = sys.argv[1]
    #
    obj = build()
    #obj = build_worm_bracket()
    if part_name:
        obj = getattr(obj, part_name)
    obj.autorender()

if __name__ == '__main__':
    main()
