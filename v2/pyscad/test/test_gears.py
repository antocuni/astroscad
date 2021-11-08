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
