from pyscad.geometry import Point, Vector

def test_Point_add():
    p1 = Point(10, 20, 30)
    v = Vector(1, 2, 3)
    p2 = p1 + v
    assert p2 == Point(11, 22, 33)

def test_Point_sub():
    p1 = Point(10, 20, 30)
    p2 = Point(1, 2, 3)
    diff = p1 - p2
    assert diff == Vector(9, 18, 27)

def test_Vector_add():
    v1 = Vector(10, 20, 30)
    v2 = Vector(1, 2, 3)
    v3 = v1 + v2
    assert v3 == Vector(11, 22, 33)

def test_Point_None():
    p1 = Point(10, 20, -100)
    bottom = Point(None, None, 30)
    v = bottom - p1
    assert v == Vector(0, 0, 130)
    assert p1 + v == Point(10, 20, 30)
