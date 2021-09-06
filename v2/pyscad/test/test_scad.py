import pytest
import re
from pyscad.scad import Cube
from pyscad.geometry import Point
from pyscad.util import InvalidAnchorError

class TestAnchors:

    def test_cube(self):
        c = Cube(2, 4, 6, center='xyz')
        assert c.O == Point.O
        assert c.pmin == Point(-1, -2, -3)
        assert c.pmax == Point(1, 2, 3)

    def test_invalidate(self):
        c = Cube(2, 4, 6, center='xyz')
        c.invalidate_anchors()
        with pytest.raises(AttributeError):
            c.I_dont_exist
        #
        with pytest.raises(InvalidAnchorError) as exc:
            c.O
        msg = str(exc.value)
        lines = msg.splitlines()
        assert lines[0] == 'AnchorPoints have been invalidated here:'
        # msg contains a stack_trace: check that the last entry is the call to
        # invalidate_anchors()
        assert re.search(r'File ".*", line .* in test_invalidate', lines[-2])
        assert lines[-1] == '        c.invalidate_anchors()'

    def test_translate(self):
        c = Cube(2, 4, 6, center='xyz')
        c.translate(10, 20, 30)
        assert c.O == Point(10, 20, 30)
        assert c.pmin == Point(9, 18, 27)
        assert c.pmax == Point(11, 22, 33)
        assert c.left == Point(9, None, None)

    def test_move_to(self):
        c = Cube(2, 4, 6, center='xyz')
        c.move_to(O=Point(10, 20, 30))
        assert c.O == Point(10, 20, 30)
        assert c.pmin == Point(9, 18, 27)
        assert c.pmax == Point(11, 22, 33)
        #
        c.move_to(O=Point(100, 200, 300))
        assert c.O == Point(100, 200, 300)
        assert c.pmin == Point(99, 198, 297)
        assert c.pmax == Point(101, 202, 303)
