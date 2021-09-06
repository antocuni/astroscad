from pyscad.scad import Cube
from pyscad.geometry import Point

class TestAnchors:

    def test_cube(self):
        c = Cube(2, 4, 6, center='xyz')
        assert c.O == Point.O
        assert c.pmin == Point(-1, -2, -3)
        assert c.pmax == Point(1, 2, 3)
