from dataclasses import dataclass

def is_scalar(x):
    return isinstance(x, (int, float))

@dataclass
class Point:
    x: float
    y: float
    z: float

    def __add__(self, v):
        if is_scalar(v):
            return self + Vector(v, v, v)
        if not isinstance(v, Vector):
            return NotImplemented
        x = self.x
        y = self.y
        z = self.z
        if x is not None: x += v.x
        if y is not None: y += v.y
        if z is not None: z += v.z
        return Point(x, y, z)

    def __sub__(self, p):
        if is_scalar(p):
            return self + (-p)
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

Point.O = Point(0, 0, 0) # origin

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

    def __mul__(self, k):
        if is_scalar(k):
            return Vector(self.x*k, self.y*k, self.z*k)
        return NotImplemented

    def __truediv__(self, k):
        if is_scalar(k):
            return Vector(self.x/k, self.y/k, self.z/k)
        return NotImplemented


class AnchorPoints:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not isinstance(value, Point):
                raise TypeError(f'{key}: a Point is required')
            setattr(self, key, value)

    def has_point(self, name):
        return name in self.__dict__

    def set_bounding_box(self, *points, set_center=True):
        """
        Set standard anchors for a bounding box which contains all the given
        points.

          - pmin, pmax: lower-left and upper-right points
          - left, right: min and max planes on the X axis
          - front, back: min and max planes on the Y axis
          - bottom, top: min and max planes on the Z axis

        If set_center == True, it also set a 'center' anchor point which is in
        the middle of the diagonal connecting pmin and pmax.
        """
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        zs = [p.z for p in points]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        zmin, zmax = min(zs), max(zs)
        self.pmin   = Point(xmin, ymin, zmin)
        self.pmax   = Point(xmax, ymax, zmax)
        self.left   = Point(xmin, None, None)
        self.right  = Point(xmax, None, None)
        self.front  = Point(None, ymin, None)
        self.back   = Point(None, ymax, None)
        self.bottom = Point(None, None, zmin)
        self.top    = Point(None, None, zmax)
        if set_center:
            self.center = self.pmin + (self.pmax - self.pmin)/2

    def __iter__(self):
        for value in self.__dict__.values():
            if isinstance(value, Point):
                yield value

    def translate(self, v):
        for key, p in self.__dict__.items():
            if not isinstance(p, Point):
                continue
            newp = p + v
            setattr(self, key, newp)

    def copy_from(self, src):
        if not isinstance(src, AnchorPoints):
            raise TypeError
        for key, p in src.__dict__.items():
            if isinstance(p, Point):
                setattr(self, key, p)
