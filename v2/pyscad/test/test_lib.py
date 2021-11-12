from pyscad import Cube, Cylinder, ImportScad, bolt_hole, Union, Point, CustomObject
from pyscad.lib.bearing import Bearing
from pyscad.lib.misc import TeflonGlide
from pyscad.lib.photo import Manfrotto_200PL
from .test_render import OpenSCADTest


class TestLib(OpenSCADTest):

    def test_bearing(self):
        obj = Union()
        obj += Bearing('608')
        obj += Bearing('608').translate(x=25).show_bounding_box()
        self.check(obj, distance=200)

    def test_teflon_glide(self):
        obj = CustomObject()
        obj.glide1 = TeflonGlide()
        obj.glide2 = TeflonGlide().translate(x=25).show_bounding_box()
        obj.cyl = Cylinder(d=obj.glide1.d, h=obj.glide1.h).translate(x=-25)
        self.check(obj, distance=200)

    def test_manfrotto_200PL(self):
        obj = CustomObject()
        obj.plate = Manfrotto_200PL().show_bounding_box()
        obj -= Cylinder(d=10, h=20).move_to(center=obj.plate.center).mod()
        self.check(obj, distance=400)

