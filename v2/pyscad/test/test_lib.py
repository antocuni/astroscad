from pyscad import Cube, Cylinder, ImportScad, bolt_hole, Union, Point
from pyscad.lib.bearing import Bearing
from .test_render import OpenSCADTest


class TestLib(OpenSCADTest):

    def test_bearing(self):
        obj = Union()
        obj += Bearing('608')
        obj += Bearing('608').translate(x=25).show_bounding_box()
        self.check(obj, distance=200)
