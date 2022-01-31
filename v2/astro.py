#!./venv/bin/python3

import sys
import math
import os
from pyscad import (Cube, Cylinder, Sphere, Point, Union, CustomObject, EPS,
                    TCone, Vector, PySCADObject)
from pyscad.shapes import DonutSlice
from pyscad.lib.misc import TeflonGlide, RoundHole, Washer
from pyscad.lib.bearing import Bearing
from pyscad.lib.gears import WormFactory
from pyscad.lib.photo import Manfrotto_200PL
from pyscad.lib.motors import Stepper_28BYJ48
from pyscad.util import in2mm
from pyscad import autorender

VITAMINS = True
FAST_RENDERING = False

IRON = [0.36, 0.33, 0.33]
BRASS = [0.88, 0.78, 0.5]
STEEL = [0.65, 0.67, 0.72]

def check_almost_equal(name, actual, expected):
    diff = abs(actual - expected)
    if diff < 0.01:
        return True
    print(f'** WARNING ** {name} has the wrong measure. Expected {expected:.2f}, got {actual:.2f} (diff={diff:.2f})')
    return False

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

    def highlight_screw_hole(self):
        disc = Cylinder(d=self.cyl.d+1, h=0.1)
        self.disc = disc.move_to(top=self.screw_hole_top)


class GenericPHBolt(CustomObject):
    """
    Generic countersunk photographic bolt (1/4" UNC-20).
    The relevant standard seems to be ANSI B18.3.
    """
    COLOR = STEEL
    D = in2mm(1/4)
    TOTAL_H = in2mm(1.25)
    HEAD_H = in2mm(0.161) # by spec
    HEAD_D = in2mm(0.5) # by spec. Specs says min=0.480, max=0.531
    THREAD_H = TOTAL_H - HEAD_H

    def init_custom(self):
        self.head = TCone(d1=14, d2=self.D, h=self.HEAD_H)
        self.thread = Cylinder(d=self.D, h=self.THREAD_H).move_to(bottom=self.head.top)
        self -= Cylinder(d=4.5, h=self.HEAD_H, segments=6).move_to(bottom=self.head.bottom-EPS)
        self.anchors.set_bounding_box(self.head.pmin, self.head.pmax,
                                      self.thread.pmin, self.thread.pmax)
        self.color(self.COLOR)

    def nut(self, *, axis='z'):
        d = 12.36
        h = 5.47
        hex = Cylinder(d=d, h=h, segments=6, axis=axis).color(IRON)
        hole = Cylinder(d=self.D, h=h+1, axis=axis)
        nut = hex-hole
        nut.anchors.set_bounding_box(hex.pmin, hex.pmax)
        return nut

class BrassPHBolt(GenericPHBolt):
    """
    My "brass" bolt seems to have non-standard measures, and the head is
    slightly smaller than all the other 1/4" bolts I have
    """
    COLOR = BRASS
    TOTAL_H = 49.8  # mm, measured by caliper
    HEAD_H = 3.85   # mm, measured by caliper
    HEAD_D = 11.80  # mm, measured by caliper
    THREAD_H = TOTAL_H - HEAD_H


class BearingBoltAdapter(CustomObject):

    WASHER_H = 1.5
    WASHER_D = 17
    WASHER_INNER_D = 8

    # XXX this needs more proper calibration for the actual bolt that you are
    # going to use
    BEARING_HOLE_CLEARANCE = 0.2
    BOLT_HOLE_CLEARANCE = 0.3
    BOLT_HEAD_CLEARANCE = 2

    def init_custom(self, bearing, bolt):
        self.head_h = bolt.HEAD_H + self.BOLT_HEAD_CLEARANCE
        head = Cylinder(d=self.WASHER_D, h=self.head_h)
        head -= TCone(d1=14, d2=bolt.D, h=self.head_h+EPS*2)
        self.head = head
        self.cyl = DonutSlice(d1=bolt.D + self.BOLT_HOLE_CLEARANCE,
                              d2=bearing.hole_d - self.BEARING_HOLE_CLEARANCE,
                              h=bearing.h + self.WASHER_H).move_to(bottom=head.top)

        self.color('white')
        self.anchors.set_bounding_box(self.head.pmin, self.head.pmax,
                                      self.cyl.pmin, self.cyl.pmax)

        if VITAMINS:
            washer = Washer(d1=self.WASHER_INNER_D, d2=self.WASHER_D, h=self.WASHER_H)
            self.washer = washer.move_to(bottom=self.head.top)


class BasePlate(CustomObject):

    BEARING_RIM = 5
    _color = 'SandyBrown'

    def init_custom(self, bearing, adapter, photo_plate):
        self.d = 80
        # the cylinder must be large enough to cover the whole photo plate,
        pp_dim = photo_plate.pmax - photo_plate.pmin
        min_d = math.hypot(pp_dim.x, pp_dim.y)
        assert self.d > min_d

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
             adapter.head_h +
             2)
        self.body = Cylinder(d=self.d, h=h).color(self._color) #.mod('#')
        self.anchors.rim_bottom = self.body.top - self.BEARING_RIM
        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)

    def make_bracket(self, bearing, photo_plate, myworm, stepper_spur):
        self.bracket = MotorBracket(self, myworm, stepper_spur)
        #
        # make holes
        # big hole where to put the bearing. h=100 means "very long"
        self -= bearing.hole(h=100, extra_walls=1)\
            .move_to(top=self.body.top - self.BEARING_RIM)

        # screw holes to attach the photo plate
        pp = photo_plate
        for p in (pp.hole3, pp.hole6, pp.hole9, pp.hole12):
            screw_hole = RoundHole(d=3, h=18, extra_walls=1)
            self -= screw_hole.move_to(center=p, bottom=self.body.bottom-EPS)

        # groove for the manfrotto plate -- DISABLED
        ## groove = photo_plate.make_rubber_pad_groove()
        ## self -= groove.move_to(bottom=self.body.bottom-EPS)

        # smaller hole to make the bearing accessible from the top
        self -= Cylinder(d=bearing.d-5, h=100)


class RotatingPlate(CustomObject):

    GROOVE_H = 1

    def init_custom(self, bolt):
        self.spur = WormFactory.spur(teeth=70, h=7, bore_d=bolt.D+0.1, optimized=False,
                                     fast_rendering=FAST_RENDERING).color('violet')#.mod()
        #
        glides = []
        for angle in (0, 120, 240):
            glide = TeflonGlide()
            r = (self.spur.d - glide.d) / 2 - 3
            angle = math.radians(angle)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            groove = glide.make_groove(self.GROOVE_H + EPS)
            groove.move_to(
                center=Point(x=x, y=y, z=None),
                top=self.spur.bottom + self.GROOVE_H
            )
            hole = RoundHole(d=2.9, h=100).move_to(center=groove.center)
            #
            self -= groove
            self -= hole
            glide.move_to(
                center=groove.center,
                top=groove.top
            )
            glides.append(glide)

        if VITAMINS:
            self.glides = glides
        self.anchors.set_bounding_box(self.spur.pmin, self.spur.pmax,
                                      glides[0].pmin, glides[0].pmax)



class SmallWormFactory(WormFactory):
    module = 1

class MyWorm(CustomObject):

    def init_custom(self, *, h, axis):
        self.h = h
        self.axis = axis
        worm = WormFactory.worm(h=h, bore_d=0, axis=axis,
                                fast_rendering=FAST_RENDERING)
        self.worm = worm.mod('%')
        self.anchors.set_bounding_box(worm.pmin, worm.pmax)

    def for_print(self, worm_shaft):
        return MyWormForPrint(h=self.h, axis=self.axis, worm_shaft=worm_shaft)


class MyWormForPrint(CustomObject):

    def init_custom(self, *, h, axis, worm_shaft):
        worm1 = WormFactory.worm(h=h, bore_d=0, axis=axis)
        worm2 = WormFactory.worm(h=h, bore_d=0, axis=axis)
        self.worm1 = worm1
        self.worm2 = worm2.tr(x=h+2)
        # remove the lower half of the worms
        self -= Cube(100, worm1.d+5, worm1.d+5).move_to(top=worm1.center)

        # cut a squared section to attach the worm on the worm shaft
        side = worm_shaft.PLACEHOLDER_SIDE + 1.5
        self -= Cube(100, side, side)


class WormShaft(CustomObject):
    # total length of the Shaft, "bearing to bearing" (including the washers)
    LENGTH = 66
    color = 'LawnGreen'

    WASHER_ID = 4.20
    WASHER_OD = 8.88
    WASHER_H = 0.84

    PLACEHOLDER_SIDE = 5 # section of the square placeholder

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
        spur = SmallWormFactory.spur(teeth=20, h=h_spur, axis=axis, optimized=False,
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

        if VITAMINS:
            self.lwasher = lwasher
            self.rwasher = rwasher


    def washers(self, *, n):
        # we simulate n washers by creating a single thicker washer
        return Washer(d1=self.WASHER_ID, d2=self.WASHER_OD,
                      h=self.WASHER_H*n, axis='x', color='white')



class StepperSpur(CustomObject):

    color = 'pink'
    SHAFT_H = 5.68

    def init_custom(self, myworm):
        spur = SmallWormFactory.spur(teeth=10, h=3, axis='x',
                                     fast_rendering=FAST_RENDERING)
        d = Stepper_28BYJ48._SBD - 2
        shaft = Cylinder(d=d, h=self.SHAFT_H, axis='x').move_to(right=spur.left)
        self.spur = spur.color(self.color)
        self.shaft = shaft.color(self.color)

        hole = Stepper_28BYJ48.make_shaft_hole(h=self.SHAFT_H)
        self -= hole.move_to(left=shaft.left-EPS).mod()

        self.anchors.set_bounding_box(self.spur.pmin, self.spur.pmax)


class MotorBracket(CustomObject):
    """
    NOTE: this MUST be printed together with the baseplate
    """

    def init_custom(self, baseplate, worm_shaft, stepper_spur):
        lb = Bearing('604', axis='x')    # left bearing
        rb = Bearing('604', axis='x')    # right bearing
        lpil = self.pillar(lb, 'left')   # left pillar
        rpil = self.pillar(rb, 'right')  # right pillar
        self.lpil = lpil.move_to(socket_center=worm_shaft.center, left=baseplate.left)
        self.rpil = rpil.move_to(socket_center=worm_shaft.center, right=baseplate.right)
        lb.move_to(center=worm_shaft.center, left=lpil.socket_left)
        rb.move_to(center=worm_shaft.center, right=rpil.socket_right)
        #
        #
        # sanity check: check that the worm_shaft (including the washers) fit
        # exactly the bearing-to-bearing distance
        expected_length = rb.left.x - lb.right.x
        check_almost_equal('worm_shaft.LENGTH', worm_shaft.LENGTH, expected_length)

        motor_mount = Cube(lpil.size.x, 30, lpil.size.z).color('cyan')
        motor_mount.move_to(top=lpil.top, back=lpil.front+EPS, left=lpil.left)
        self.motor_mount = motor_mount

        floor_sx = rpil.right.x - lpil.left.x
        floor_sy = abs(rpil.front.y)
        check_almost_equal('floor_sx', floor_sx, baseplate.d)
        lfloor = Cube(floor_sx, floor_sy, 5).color('cyan')
        self.lfloor = lfloor.move_to(left=lpil.left,
                                     bottom=baseplate.bottom+EPS,
                                     back=baseplate.center)
        #
        # we want to place the stepper-spur so that meshes with the worm-spur,
        # but we need to be careful else the stepper mounting holes touch the
        # bearing
        dist = (stepper_spur.spur.r + worm_shaft.spur.r)
        a = math.radians(260)
        v = Vector(0, dist*math.sin(a), dist*math.cos(a))
        stepper_spur.move_to(center=worm_shaft.spur.center + v, right=worm_shaft.spur.right)
        #
        stepper = Stepper_28BYJ48()
        stepper.move_to(
            shaft=stepper_spur.spur.center,
            right=self.lpil.left)
        self -= stepper.make_mounting_holes(h=50, d=2.9)

        expected_stepper_spur_shaft_h = stepper_spur.spur.left.x - stepper.right.x - 4
        check_almost_equal('stepper spur shaft',
                           stepper_spur.SHAFT_H,
                           expected_stepper_spur_shaft_h)

        if VITAMINS:
            self.lb = lb
            self.rb = rb
            self.stepper = stepper

    def pillar(self, bearing, which, *, sy=None):
        assert which in ('left', 'right')
        # extra borders around the bearing
        bz = 1.5
        by = 3
        sx = bearing.h + 4
        if sy is None:
            sy = bearing.d + by*2 # default value
        sz = 37 # it should be computed, not hard coded
        p = Cube(sx, sy, sz).color('cyan')
        #
        socket = bearing.hole(bearing.h + 1)
        if which == 'left':
            socket.move_to(top=p.top-bz, right=p.right+EPS, back=p.back-by)
        else:
            socket.move_to(top=p.top-bz, left=p.left-EPS, back=p.back-by)
        p -= socket
        #
        p -= RoundHole(d=10, h=100, axis='x').move_to(center=socket.center)
        p.anchors.socket_center = socket.center
        p.anchors.socket_left = socket.left
        p.anchors.socket_right = socket.right
        return p


def build():
    obj = CustomObject()
    bearing = Bearing('608')
    bolt = BrassPHBolt()
    #bolt = GenericPHBolt()
    adapter = BearingBoltAdapter(bearing, bolt)
    photo_plate = Manfrotto_200PL(with_holes=True)

    baseplate = BasePlate(bearing, adapter, photo_plate).move_to(bottom=Point.O)
    bearing = bearing.move_to(top=baseplate.rim_bottom)
    #
    obj.adapter = adapter.move_to(top=bearing.top)
    bolt.move_to(bottom=adapter.bottom)

    rplate = RotatingPlate(bolt)
    obj.rplate = rplate.move_to(bottom=baseplate.body.top) #+25)

    myworm = MyWorm(h=25, axis='x')
    myworm.move_to(center=rplate.spur.center, back=rplate.spur.front)
    obj.myworm = myworm

    worm_shaft = WormShaft(axis='x').move_to(worm_center=myworm.center)
    obj.worm_shaft = worm_shaft

    stepper_spur = StepperSpur(worm_shaft) # note: this is moved inside make_bracket
    baseplate.make_bracket(bearing, photo_plate, worm_shaft, stepper_spur)
    obj.baseplate = baseplate
    obj.stepper_spur = stepper_spur

    #compute_ratio(obj)

    if VITAMINS:
        obj.bolt = bolt
        obj.bearing = bearing
        obj.nut = bolt.nut().move_to(bottom=bearing.top+EPS)
        obj.photo_plate = photo_plate.move_to(top=obj.baseplate.bottom-EPS)\
                                     .color(IRON, 0.7)
        ball_head = BallHead().move_to(bottom=rplate.top)
        diff = bolt.top.z - ball_head.screw_hole_top.z
        if diff > 0:
            ball_head.mod()
            ball_head.highlight_screw_hole()
            print(f'** WARNING **: the bolt is too long for the ball head: {diff:.2f}')
        diff = bolt.top.z - rplate.top.z
        if diff < 8:
            print(f'** WARNING **: the bolt is too short for the 1/4"-3/8" adapter: {diff:.2f}')
        #obj.ball_head = ball_head

    return obj

def compute_ratio(obj):
    main_worm = obj.myworm.worm
    main_spur = obj.rplate.spur
    ratio1 = main_spur.teeth / main_worm.thread_starts
    #
    motor_spur = obj.stepper_spur.spur
    myworm_spur = obj.myworm.spur
    ratio2 = myworm_spur.teeth / motor_spur.teeth
    #
    total_ratio = ratio1 * ratio2
    steps_per_360 = 512*8 * total_ratio
    steps_per_sec = steps_per_360 / (24*60*60)
    sec_per_steps = 1 / steps_per_sec
    print(f'Total ratio: 1:{total_ratio} -- 1 step every {sec_per_steps:.4f}s')


def main():
    global FAST_RENDERING
    global VITAMINS
    parts = None
    if '--fast' in sys.argv:
        FAST_RENDERING = True
    if '--no-vitamins' in sys.argv:
        VITAMINS = False

    if len(sys.argv) >= 2:
        parts = sys.argv[1:]
        if '--fast' in parts:
            parts.remove('--fast')
        if '--no-vitamins' in parts:
            parts.remove('--no-vitamins')
    #
    obj = build()
    #obj = build_worm_bracket()
    if parts and parts[0].startswith('-'):
        # show everything APART the parts which are given
        hidden_parts = [p[1:] for p in parts] # remove the '-' from everywhere
        new_obj = CustomObject()
        for part_name, part_obj in obj.__dict__.items():
            if isinstance(part_obj, PySCADObject):
                if part_name not in hidden_parts:
                    print(part_name)
                    setattr(new_obj, part_name, part_obj)
        obj = new_obj

    elif parts:
        # show only the parts which are given
        new_obj = CustomObject()
        for part_name in parts:
            if part_name == 'myworm':
                # special case
                new_obj.myworm = obj.myworm.for_print(obj.worm_shaft)
            else:
                part_obj = getattr(obj, part_name)
                setattr(new_obj, part_name, part_obj)
        obj = new_obj

    # fn=100 is needed to make sure that cura makes fully circular top/bottom patterns
    obj.autorender(fn=100)

if __name__ == '__main__':
    main()
