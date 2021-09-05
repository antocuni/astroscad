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
        return Vector(x=self.x-p.x,
                      y=self.y-p.y,
                      z=self.z-p.z)

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
