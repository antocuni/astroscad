from pyscad.geometry import Point, Vector, AnchorPoints

class TestPointVector:

    def test_Point_add(self):
        p1 = Point(10, 20, 30)
        v = Vector(1, 2, 3)
        p2 = p1 + v
        assert p2 == Point(11, 22, 33)

    def test_Point_add_None(self):
        p1 = Point(10, None, None)
        v = Vector(1, 2, 3)
        p2 = p1 + v
        assert p2 == Point(11, None, None)

    def test_Point_add_scalar(self):
        p1 = Point(1, 2, 3)
        p2 = p1 + 10
        assert p2 == Point(11, 12, 13)

    def test_Vector_add(self):
        v1 = Vector(10, 20, 30)
        v2 = Vector(1, 2, 3)
        v3 = v1 + v2
        assert v3 == Vector(11, 22, 33)

    def test_sub(self):
        p1 = Point(10, 20, 30)
        p2 = Point(1, 2, 3)
        diff = p1 - p2
        assert diff == Vector(9, 18, 27)

    def test_sub_with_None(self):
        p1 = Point(10, 20, -100)
        bottom = Point(None, None, 30)
        v = bottom - p1
        assert v == Vector(0, 0, 130)
        assert p1 + v == Point(10, 20, 30)

    def test_Point_sub_scalar(self):
        p1 = Point(11, 12, 13)
        p2 = p1 - 10
        assert p2 == Point(1, 2, 3)


class TestAnchorPoints:

    def test_init(self):
        a = AnchorPoints(p1=Point(1, 2, 3),
                         p2=Point(4, 5, 6))
        assert a.p1 == Point(1, 2, 3)
        assert a.p2 == Point(4, 5, 6)

    def test_set_bounding_box(self):
        p1 = Point(1, 2, -3)
        p2 = Point(-1, -2, 3)
        a = AnchorPoints()
        a.set_bounding_box(p1, p2)
        assert a.pmin == Point(-1, -2, -3)
        assert a.pmax == Point(1, 2, 3)
        assert a.left == Point(-1, None, None)
        assert a.right == Point(1, None, None)
        assert a.front == Point(None, -2, None)
        assert a.back == Point(None, 2, None)
        assert a.bottom == Point(None, None, -3)
        assert a.top == Point(None, None, 3)

    def test_iter(self):
        p1 = Point(1, 2, 3)
        p2 = Point(4, 5, 6)
        p3 = Point(7, 8, 9)
        a = AnchorPoints(p1=p1, p2=p2, p3=p3)
        a.name = 'Hello'
        assert list(a) == [p1, p2, p3]

    def test_translate(self):
        a = AnchorPoints(p1=Point(1, 2, 3),
                         p2=Point(4, 5, 6))
        v = Vector(10, 20, 30)
        a.translate(v)
        assert a.p1 == Point(11, 22, 33)
        assert a.p2 == Point(14, 25, 36)

    def test_copy_from(self):
        src = AnchorPoints(p1=Point(1, 2, 3),
                           p2=Point(4, 5, 6))
        dst = AnchorPoints()
        dst.copy_from(src)
        assert dst.p1 == src.p1
        assert dst.p2 == src.p2
