from dataclasses import dataclass
from .geometry import Vector

@dataclass
class Camera:
    vpt: Vector  # viewport translation
    vpr: Vector  # viewport rotation
    distance: float

    def __init__(self, vpt, vpr, distance):
        if isinstance(vpt, list):
            vpt = Vector(*vpt)
        if isinstance(vpr, list):
            vpr = Vector(*vpr)
        self.vpt = vpt
        self.vpr = vpr
        self.distance = distance

    def with_distance(self, distance):
        return self.__class__(self.vpt, self.vpr, distance)

    def as_cmdline(self):
        parts = [self.vpt.x, self.vpt.y, self.vpt.z,
                 self.vpr.x, self.vpr.y, self.vpr.z,
                 self.distance]
        parts = [str(p) for p in parts]
        return ','.join(parts)

Camera.DEFAULT = Camera([0, 0, 0], [ 55, 0,  25], 140)
Camera.RIGHT   = Camera([0, 0, 0], [ 90, 0,  90], 140)
Camera.TOP     = Camera([0, 0, 0], [  0, 0,   0], 140)
Camera.BOTTOM  = Camera([0, 0, 0], [180, 0,   0], 140)
Camera.LEFT    = Camera([0, 0, 0], [ 90, 0, 270], 140)
Camera.FRONT   = Camera([0, 0, 0], [ 90, 0,   0], 140)
Camera.BACK    = Camera([0, 0, 0], [ 90, 0, 180], 140)
