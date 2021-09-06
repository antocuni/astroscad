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


class AnchorPoints:

    def __init__(self, **kwargs):
        self.points = {}
        for key, value in kwargs.items():
            if not isinstance(value, Point):
                raise TypeError(f'{key}: a Point is required')
            self.points[key] = value

    def set_bounding_box(self, p1, p2):
        """
        Set standard anchors for a bounding box delimited by p1, p2.

          - pmin, pmax: lower-left and upper-right points
          - left, right: min and max planes on the X axis
          - front, back: min and max planes on the Y axis
          - bottom, top: min and max planes on the Z axis
        """
        xmin, xmax = sorted((p1.x, p2.x))
        ymin, ymax = sorted((p1.y, p2.y))
        zmin, zmax = sorted((p1.z, p2.z))
        self.points['pmin']   = Point(xmin, ymin, zmin)
        self.points['pmax']   = Point(xmax, ymax, zmax)
        self.points['left']   = Point(xmin, None, None)
        self.points['right']  = Point(xmax, None, None)
        self.points['front']  = Point(None, ymin, None)
        self.points['back']   = Point(None, ymax, None)
        self.points['bottom'] = Point(None, None, zmin)
        self.points['top']    = Point(None, None, zmax)

    def __iter__(self):
        for value in self.points.values():
            if isinstance(value, Point):
                yield value

    def translate(self, v):
        for key, p in self.points.items():
            if not isinstance(p, Point):
                continue
            newp = p + v
            setattr(self, key, newp)

    def __getattr__(self, name):
        try:
            return self.points[name]
        except KeyError:
            raise AttributeError(name)
