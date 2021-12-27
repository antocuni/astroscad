from pyscad import Cube, Cylinder, ImportScad, bolt_hole, Union, Point
from pyscad.lib.gears import WormFactory, _gears
from .test_render import OpenSCADTest


class TestGear(OpenSCADTest):

    def test_spur_simple(self):
        obj = Union()
        spur = WormFactory.spur(teeth=24, h=2, bore_d=3.2)
        obj += spur
        obj += Cylinder(r=spur.r, h=1).color('red', 0.3).move_to(bottom=spur.top)
        self.check(obj)

    def test_spur_other_axes(self):
        obj = Union()
        spur_x = WormFactory.spur(teeth=24, h=2, bore_d=3.2, axis='x').tr(z=15)
        spur_y = WormFactory.spur(teeth=24, h=2, bore_d=3.2, axis='y').tr(z=-15)
        obj += spur_x.show_bounding_box()
        obj += spur_y.show_bounding_box()
        self.check(obj, distance=160)

    def test_worm_simple(self):
        obj = Union()
        worm = WormFactory.worm(h=15, bore_d=4)
        obj += worm.show_bounding_box()
        obj += Cylinder(r=worm.r, h=1).color('red', 0.3).move_to(bottom=worm.top)
        self.check(obj)

    def test_worm_other_axes(self):
        obj = Union()
        worm_x = WormFactory.worm(h=15, bore_d=4, axis='x').tr(z=15)
        worm_y = WormFactory.worm(h=15, bore_d=4, axis='y').tr(z=-15)
        obj += worm_x.show_bounding_box()
        obj += worm_y.show_bounding_box()
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
        worm = WormFactory.worm(h=15, bore_d=0, axis='y')
        root += spur
        root += worm.move_to(left=spur.right)
        self.check(root)
