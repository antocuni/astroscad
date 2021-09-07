import pytest
import re
from pyscad.scad import Cube, Cylinder, Sphere, Composite
from pyscad.geometry import Point
from pyscad.util import InvalidAnchorError

class TestAnchors:

    def test_Cube(self):
        c = Cube(2, 4, 6)
        assert c.center == Point.O
        assert c.pmin == Point(-1, -2, -3)
        assert c.pmax == Point(1, 2, 3)

    def test_invalidate(self):
        c = Cube(2, 4, 6)
        c.invalidate_anchors()
        with pytest.raises(AttributeError):
            c.I_dont_exist
        #
        with pytest.raises(InvalidAnchorError) as exc:
            c.center
        msg = str(exc.value)
        lines = msg.splitlines()
        assert lines[0] == 'AnchorPoints have been invalidated here:'
        # msg contains a stack_trace: check that the last entry is the call to
        # invalidate_anchors()
        assert re.search(r'File ".*", line .* in test_invalidate', lines[-2])
        assert lines[-1] == '        c.invalidate_anchors()'

    def test_translate(self):
        c = Cube(2, 4, 6)
        c.translate(10, 20, 30)
        assert c.center == Point(10, 20, 30)
        assert c.pmin == Point(9, 18, 27)
        assert c.pmax == Point(11, 22, 33)
        assert c.left == Point(9, None, None)

    def test_move_to(self):
        c = Cube(2, 4, 6)
        c.move_to(center=Point(10, 20, 30))
        assert c.center == Point(10, 20, 30)
        assert c.pmin == Point(9, 18, 27)
        assert c.pmax == Point(11, 22, 33)
        #
        c.move_to(center=Point(100, 200, 300))
        assert c.center == Point(100, 200, 300)
        assert c.pmin == Point(99, 198, 297)
        assert c.pmax == Point(101, 202, 303)

    def test_move_to_recursive(self):
        class Puppet(Composite):
            def make(self):
                super().make()
                body = Cube(10, 10, 10)
                head = Sphere(d=5).move_to(bottom=body.top)
                self.add(body=body, head=head)
                self.anchors.center = body.center

        puppet = Puppet()
        assert puppet.center == Point.O
        assert puppet.body.center == Point.O
        assert puppet.head.center == Point(0, 0, 7.5)
        #
        puppet.move_to(center=Point(20, 20, 20))
        assert puppet.center == Point(20, 20, 20)
        assert puppet.body.center == Point(20, 20, 20)
        assert puppet.head.center == Point(20, 20, 27.5)


    def test_Cylinder(self):
        c = Cylinder(h=10, d=30)
        assert c.center == Point.O
        assert c.pmin == Point(-15, -15, -5)
        assert c.pmax == Point(15, 15, 5)
        #
        c2 = Cylinder(h=10, r=15)
        assert c2.center == Point.O
        assert c2.pmin == Point(-15, -15, -5)
        assert c2.pmax == Point(15, 15, 5)
