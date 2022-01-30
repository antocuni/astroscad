from pyscad import Union, Cylinder
from pyscad.shapes import DonutSlice
from .test_render import OpenSCADTest


class TestShapes(OpenSCADTest):

    def test_DonutSlice(self):
        obj = Union()
        donut_z = DonutSlice(r1=5, r2=10, h=3).show_bounding_box()
        donut_x = DonutSlice(r1=5, r2=10, h=3, axis='x').show_bounding_box()
        donut_y = DonutSlice(r1=5, r2=10, h=3, axis='y').show_bounding_box()
        obj += donut_z
        obj += donut_x.tr(x=15)
        obj += donut_y.tr(x=-25)
        self.check(obj, distance=200)
