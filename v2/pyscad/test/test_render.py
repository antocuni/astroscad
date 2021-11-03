import os
import py
import pytest
from pytest_image_diff import image_diff
from pyscad.scad import Point, Cube, Cylinder, Sphere, Composite, Union

ROOT = py.path.local(__file__).dirpath()
REFDIR = ROOT.join('screenshots').ensure(dir=True)

class OpenSCADTest:

    @pytest.fixture(autouse=True)
    def init(self, request, tmpdir):
        self.request = request
        self.tmpdir = tmpdir

    def check(self, obj):
        name = f'{self.__class__.__name__}.{self.request.node.name}'
        ref = REFDIR.join(f'{name}.png')
        actual = self.tmpdir.join(f'{name}.png')
        diff = self.tmpdir.join(f'{name}-diff.png')
        obj.render_to_collage(actual)
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
