from pyscad import Cube, Cylinder, ImportScad, bolt_hole, Union, Point
from pyscad.gears import WormFactory, _gears
from .test_render import OpenSCADTest


class TestGear(OpenSCADTest):

    def test_spur(self):
        obj = Union()
        spur = WormFactory.spur(teeth=24, h=2, bore_d=3.2)
        obj += spur
        obj += Cylinder(r=spur.r, h=1).color('red', 0.3).move_to(bottom=spur.top)
        self.check(obj)

    def test_worm(self):
        obj = Union()
        worm = WormFactory.worm(length=15, bore_d=4)
        obj += worm
        obj += Cylinder(r=worm.r, h=worm.length).color('red', 0.3).rot(x=90)
        obj += Cube(worm.r, worm.length, 2).color('green', 0.3).move_to(bottom=worm.top)
        self.check(obj)

    def test_bracket(self):
        R_WORM = 5.75877
        def bracket():
            r_worm = R_WORM
            r_gear = 12
            t = 4 # thickness*2
            w = 28
            h = 2.5
            obj = Cube(w+t, w+t,  h+t)
            obj -= Cube(w+t+1, w, 2.5)
            obj -= Cube(w+t+1, w, h+t+1).translate((w+t+1)/2)
            #
            delta = -w/4
            obj -= (
                bolt_hole(d=3.2, h=h+t)
                .tr(x=delta)
                )
            obj -= (
                bolt_hole(d=3.2, h=50)
                .rot(x=90)
                .tr(delta+r_gear+r_worm)
                )
            return obj.tr(x=-delta)

        root = Union()
        root += bracket().mod('%')
        spur = WormFactory.spur(teeth=24, h=2, bore_d=3.2)
        worm = WormFactory.worm(length=15, bore_d=0)
        root += spur
        root += worm.move_to(left=spur.right)
        self.check(root)
