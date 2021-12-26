from pyscad import Union, Cylinder
from pyscad.shapes import DonutSlice
from .test_render import OpenSCADTest


class TestShapes(OpenSCADTest):

    def test_DonutSlice(self):
        obj = Union()
        donut = DonutSlice(r1=5, r2=10, h=3)
        obj += donut.show_bounding_box()
        self.check(obj)

