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

IRON = [0.36, 0.33, 0.33]
BRASS = [0.88, 0.78, 0.5]
STEEL = [0.65, 0.67, 0.72]

M3 = 3.4
M5 = 5.5 # diameter of holes for M5 screws
PH_38 = in2mm(3/8) + 0.5  # diameter for holes of 3/8" screws

def M5_countersink_hole(h=20):
    dk = 9.3 + 0.5 # nominal d of the head + clearance
    k = 2.7 + 0.7  # nominal h of the head + clearance
    obj = CustomObject()
    obj.head = TCone(d1=M5, d2=dk, h=k)
    obj.thread = Cylinder(d=M5, h=h-k).move_to(top=obj.head.bottom+EPS)
    obj.anchors.set_bounding_box(obj.head.pmin, obj.head.pmax,
                                 obj.thread.pmin, obj.thread.pmax)
    return obj


class MyWormFactory(WormFactory):
    thread_starts = 1

class FourHoles(CustomObject):

    def init_custom(self, dist, *, d, h=100, angle=0, countersink=False):
        holes = []
        points = []
        bbox = []
        for i in range(4):
            a = math.radians(angle + i*90)
            x = dist * math.cos(a)
            y = dist * math.sin(a)
            p = Point(x, y, 0)
            if countersink:
                assert d == M5, 'countersink holes supported only for M5'
                hole = M5_countersink_hole(h=h).move_to(center=p)
            else:
                hole = Cylinder(d=d, h=h).move_to(center=p)
            holes.append(hole)
            points.append(p)
            bbox += [hole.pmin, hole.pmax]
        self.holes = holes
        self.points = points
        self.anchors.set_bounding_box(*bbox)


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
        holes = FourHoles(turntable.ihd, d=M5, countersink=True)
        holes.move_to(top=self.body.top+EPS)
        self.sub(holes=holes)
        self -= Cylinder(d=PH_38, h=6)
        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)


class SpurPlate(CustomObject):

    def init_custom(self, turntable):
        self.body = Cylinder(d=turntable.d2-1, h=2).color('pink')
        spur = WormFactory.spur(teeth=70, h=18, optimized=False,
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
            spoke = Cube(2, spur.teeth, 2).color('pink')
            spoke.move_to(top=self.body.top).rot(z=angle)
            spokes.append(spoke)
        self.spokes = spokes

        self.anchors.set_bounding_box(self.body.pmin, self.body.pmax)


class BottomPlate(CustomObject):

    PILLAR_H = 30
    BODY_H = 4

    def init_custom(self, turntable):
        self.d = turntable.d4+2
        self._ohd = turntable.ohd
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

        # motor bracket plate, which is an inset inside the body
        mb_floor = self.make_motor_bracket_floor()
        mb_floor.move_to(center=self.body.center, top=self.body.top+EPS)
        mb_holes = self.make_motor_bracket_holes()
        self.sub(mb_floor=mb_floor)
        self.sub(mb_holes=mb_holes)

        pp = Manfrotto_200PL(with_holes=True)
        pp.move_to(top=body.bottom-EPS)
        # screw holes to attach the photo plate
        for p in (pp.hole3, pp.hole6, pp.hole9, pp.hole12):
            screw_hole = RoundHole(d=3, h=18, extra_walls=1)
            self -= screw_hole.move_to(center=p, bottom=self.body.bottom-EPS)


        if VITAMINS:
            self.photo_plate = pp.color(IRON, 0.7)

        self.anchors.set_bounding_box(body.pmin, body.pmax,
                                      pillars[0].pmin, pillars[0].pmax)

    def make_motor_bracket_floor(self):
        d = self.body.d + EPS*2
        h = 2
        mb_floor = Cylinder(d=d, h=h)
        mb_floor -= Cube(d, d, h+1).tr(y=40)
        return mb_floor

    def make_motor_bracket_holes(self, h=10):
        def hole(d, ang):
            dist = self._ohd
            x = dist * math.cos(math.radians(ang))
            y = dist * math.sin(math.radians(ang))
            cyl = Cylinder(d=d, h=h).move_to(center=self.body.center)
            return cyl.tr(x=x, y=y)
        holes = CustomObject()
        holes.h1 = hole(M3, -30)
        holes.h2 = hole(M3, -150)
        holes.h5 = hole(M5, -90)
        return holes


class WormShaft(CustomObject):
    # total length of the Shaft, "bearing to bearing" (including the washers)
    LENGTH = 66
    color = 'LawnGreen'

    WASHER_ID = 4.20
    WASHER_OD = 8.88
    WASHER_H = 0.84

    PLACEHOLDER_SIDE = 5 # section of the square placeholder
    SPUR_TEETH = 21

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
        ## automatic compute the ltl, rtl
        ## ltl = self.LENGTH/2 - h_worm/2 - h_spur - lwasher.h
        ## rtl = self.LENGTH/2 - h_worm/2 - rwasher.h
        # or manually override the settings
        ltl = 14.72
        rtl = 19.56

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

        #
        # sanity check
        actual_length = rwasher.right.x - lwasher.left.x
        check_almost_equal('WormShaft.LENGTH', self.LENGTH, actual_length)

        # this hole is needed in conjunction with a 3d-printed cylindric axis:
        # if we drill a hole inside the inner axis and fix it with a stick, we
        # can attach the axis to a drill and rotate the worm very fast, useful
        # for running in the system.
        self -= Cylinder(d=2, h=10, axis='y').tr(25, 0, 0) #.mod()

        # NOTE: the bounding box of the shaft also includes the washers!
        self.anchors.set_bounding_box(spur.pmin, spur.pmax,
                                      worm.pmin, worm.pmax,
                                      r_trunk.pmin, r_trunk.pmax,
                                      lwasher.pmin, lwasher.pmax,
                                      rwasher.pmin, rwasher.pmax)
        self.anchors.worm_center = worm.center
        self.anchors.worm_back = worm.back

        if VITAMINS:
            self.lwasher = lwasher
            self.rwasher = rwasher
            shaft = Cylinder(d=4, h=92, axis='x').color(IRON)
            self.shaft = shaft.move_to(center=worm.center)

    def washers(self, *, n):
        # we simulate n washers by creating a single thicker washer
        return Washer(d1=self.WASHER_ID, d2=self.WASHER_OD,
                      h=self.WASHER_H*n, axis='x', color='white')

class StepperSpur(CustomObject):

    color = 'pink'
    SHAFT_H = 5.68
    TEETH = 7

    def init_custom(self, myworm):
        spur = WormFactory.spur(teeth=self.TEETH, h=3, axis='x',
                                fast_rendering=FAST_RENDERING)
        d = Stepper_28BYJ48._SBD - 2
        shaft = Cylinder(d=d, h=self.SHAFT_H, axis='x').move_to(right=spur.left)
        self.spur = spur.color(self.color)
        self.shaft = shaft.color(self.color)

        hole = Stepper_28BYJ48.make_shaft_hole(h=self.SHAFT_H)
        self -= hole.move_to(left=shaft.left-EPS).mod()
        self.anchors.set_bounding_box(spur.pmin, spur.pmax)

    def for_print(self):
        """
        hack hack hack. I keep it around only in case I need it again in the
        future, it's a way to print a slightly smaller spur, useful to add
        some play between two gears. It needs to comment out the
        "invalidate_anchors()" inside PySCADObject.scale
        """
        #pmin = spur.pmin
        #pmax = spur.pmax
        s = 0.9
        spur.scale(1, s, s)
        #spur.anchors.set_bounding_box(pmin, pmax)
        self.spur = spur.color(self.color)
        self.anchors.set_bounding_box(spur.pmin, spur.pmax)

        

class MotorBracket(CustomObject):

    def init_custom(self, bottom_plate, worm_shaft, stepper_spur):
        lb = Bearing('604', axis='x')    # left bearing
        rb = Bearing('604', axis='x')    # right bearing
        lb.move_to(center=worm_shaft.center, right=worm_shaft.left)
        rb.move_to(center=worm_shaft.center, left=worm_shaft.right)

        bx = 3   # extra space for the bearing rim
        bz = 1.5 # extra space above the bearing
        by = 3   # extra space around the bearing
        # compute the h so that the walls touch the mb_floor
        h = lb.top.z + bz - bottom_plate.mb_floor.bottom.z

        lwall = Cube(lb.h+bx, 50, h).color('cyan')
        lwall.move_to(right=lb.right, back=lb.back+by, top=lb.top+bz)
        self.make_bearing_socket(lwall, lb, 'right')

        rwall = Cube(5, 17, h).color('cyan')
        rwall.move_to(left=rb.left, back=rb.back+by, top=rb.top+bz)
        self.make_bearing_socket(rwall, rb, 'left')

        floor = bottom_plate.make_motor_bracket_floor()
        floor.move_to(center=bottom_plate.center, bottom=bottom_plate.mb_floor.bottom)
        floor -= bottom_plate.make_motor_bracket_holes()
        self.floor = floor.color('cyan')

        # sanity check: check that the worm_shaft (including the washers) fit
        # exactly the bearing-to-bearing distance. This should be correct by
        # construction.
        expected_length = rb.left.x - lb.right.x
        check_almost_equal('worm_shaft.LENGTH', worm_shaft.LENGTH, expected_length)

        # we want to place the stepper-spur so that meshes with the worm-spur,
        # but we need to be careful else the stepper mounting holes touch the
        # bearing
        # the "+1" is to allow a bit of play between the spurs, else they get stuck
        dist = (stepper_spur.spur.r + worm_shaft.spur.r) + 1
        a = math.radians(260)
        v = Vector(0, dist*math.sin(a), dist*math.cos(a))
        stepper_spur.move_to(center=worm_shaft.spur.center + v,
                             right=worm_shaft.spur.right)

        stepper = Stepper_28BYJ48()
        stepper.move_to(
            shaft=stepper_spur.spur.center,
            right=lwall.left)
        expected_stepper_spur_shaft_h = stepper_spur.spur.left.x - stepper.right.x - 4
        check_almost_equal('stepper spur shaft',
                           stepper_spur.SHAFT_H,
                           expected_stepper_spur_shaft_h)

        self.lwall = lwall
        self.rwall = rwall
        self -= stepper.make_mounting_holes(h=50, d=3.1)

        # make a dent in the bottom_plate and the motor_bracket to make sure
        # that the stepper can fit
        self -= self.make_space_for_stepper(stepper)
        bottom_plate -= self.make_space_for_stepper(stepper, h_clearance=4)

        if VITAMINS:
            self.lb = lb
            self.rb = rb
            self.stepper = stepper

    def make_bearing_socket(self, wall, bearing, where):
        socket = bearing.hole(bearing.h)
        if where == 'left':
            socket.move_to(center=bearing.center, left=wall.left-EPS)
        else:
            socket.move_to(center=bearing.center, right=wall.right+EPS)
        wall -= socket
        wall -= RoundHole(d=10, h=100, axis='x').move_to(center=socket.center)

    def make_space_for_stepper(self, stepper, h_clearance=0):
        clearance = 3
        body = Cylinder(d=stepper._MBD+2, h=stepper._MBH+h_clearance, axis='x')
        body.move_to(center=stepper.center).tr(x=-EPS)
        return body


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
    bottom_plate = bottom_plate.move_to(top=turntable.bottom)

    worm = WormFactory.worm(h=25, bore_d=0, axis='x', fast_rendering=FAST_RENDERING)
    worm.mod('%')
    obj.worm = worm.move_to(bottom=spur_plate.spur.bottom, back=spur_plate.spur.front)
    if worm.top.z+1 >= turntable.bottom.z:
        # the +1 is to count the addendum circle
        print('WARNING, the worm touches the turntable!')
    if worm.top.z+1 >= spur_plate.body.bottom.z:
        print('WARNING, the worm touches the spur plate')

    worm_shaft = WormShaft(axis='x').move_to(worm_center=worm.center)
    obj.worm_shaft = worm_shaft
    if worm_shaft.spur.top.z+1 >= spur_plate.body.bottom.z:
        print('WARNING, the worm_shaft.spur touches the spur plate')


    stepper_spur = StepperSpur(worm_shaft) # note: this is placed by MotorBracket
    obj.motor_bracket = MotorBracket(bottom_plate, worm_shaft, stepper_spur)
    obj.stepper_spur = stepper_spur
    obj.bottom_plate = bottom_plate

    return obj


if __name__ == '__main__':
    main(build)

