from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

    def __add__(self, v):
        if not isinstance(v, Vector):
            return NotImplemented
        return Point(x=self.x+v.x,
                     y=self.y+v.y,
                     z=self.z+v.z)

    def __sub__(self, p):
        if not isinstance(p, Point):
            return NotImplemented
        dx = dy = dz = 0
        if self.x is not None and p.x is not None:
            dx = self.x - p.x
        if self.y is not None and p.y is not None:
            dy = self.y - p.y
        if self.z is not None and p.z is not None:
            dz = self.z - p.z
        return Vector(dx, dy, dz)

@dataclass
class Vector:
    x: float
    y: float
    z: float

    def __add__(self, v):
        if not isinstance(v, Vector):
            return NotImplemented
        return Vector(x=self.x+v.x,
                      y=self.y+v.y,
                      z=self.z+v.z)
