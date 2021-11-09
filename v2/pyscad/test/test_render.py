import os
import py
import pytest
from pytest_image_diff import image_diff
from pyscad.scad import Point, Cube, Cylinder, Sphere, Union, TCone, CustomObject
from pyscad.autorender import run_openscad_maybe

ROOT = py.path.local(__file__).dirpath()
REFDIR = ROOT.join('screenshots').ensure(dir=True)

class OpenSCADTest:

    @pytest.fixture(autouse=True)
    def init(self, request, tmpdir):
        self.request = request
        self.tmpdir = tmpdir

    def check(self, obj, distance=None):
        name = f'{self.__class__.__name__}.{self.request.node.name}'
        ref = REFDIR.join(f'{name}.png')
        actual = self.tmpdir.join(f'{name}.png')
        diff = self.tmpdir.join(f'{name}-diff.png')
        if self.request.config.option.show_scad:
            obj.render_to_file('/tmp/pytest.scad')
            run_openscad_maybe('/tmp/pytest.scad')
        #
        obj.render_to_collage(actual, distance)
        # with --save-ref-img we just save the screenshot as the new reference
        # image and be happy
        if self.request.config.option.save_ref_img:
            actual.copy(ref)
            return
        #
        if ref.check(exists=False):
            raise Exception(f'Reference does not exist: {ref.relto(ROOT)}')
        res = image_diff._diff(str(ref), str(actual), str(diff))
        if res != 0:
            os.system(f'eog "{diff}" &')
        assert res == 0

class TestBasic(OpenSCADTest):

    def test_cube(self):
        obj = Cube(10, 10, 10)
        self.check(obj)

    def test_move_to(self):
        obj = Union()
        x = Cube(10)
        obj += x.move_to(center=Point(10, 10, 10))
        obj += Cube(3).color('red').move_to(center=x.center, bottom=x.top)
        obj += Cube(3).color('green').move_to(center=x.center, left=x.right)
        obj += Cube(3).color('blue').move_to(center=x.center, top=x.bottom)
        self.check(obj)

    def test_sphere(self):
        obj = Union()
        x = Sphere(d=10)
        obj += x
        obj += Cube(10).color('red').move_to(left=x.right)
        self.check(obj)

    def test_show_bounding_box(self):
        obj = Union()
        x = Sphere(d=10)
        x.show_bounding_box()
        obj += x
        self.check(obj)

    def test_cylinder(self):
        obj = CustomObject()
        obj.cube = Cube(6)
        obj.a = Cylinder(r=3, h=20).color('red', 0.3).move_to(bottom=obj.cube.top)
        obj.b = Cylinder(r=3, hx=20).color('green', 0.3).move_to(left=obj.cube.right)
        obj.c = Cylinder(r=3, hy=20).color('blue', 0.3).move_to(front=obj.cube.back)
        assert obj.a.h == obj.b.h == obj.c.h == 20
        self.check(obj)

    def test_tcone(self):
        obj = CustomObject()
        obj.cube = Cube(6)
        obj.a = TCone(r1=3, r2=1, h=10).color('red', 0.3).move_to(bottom=obj.cube.top)
        obj.b = TCone(r1=3, r2=1, hx=10).color('green', 0.3).move_to(left=obj.cube.right)
        obj.c = TCone(r1=3, r2=1, hy=10).color('blue', 0.3).move_to(front=obj.cube.back)
        assert obj.a.h == obj.b.h == obj.c.h == 10
        assert obj.a.r1 == 3
        assert obj.a.r2 == 1
        assert obj.a.d1 == 6
        assert obj.a.d2 == 2
        self.check(obj)
