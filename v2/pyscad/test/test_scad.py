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
