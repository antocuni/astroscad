from ..scad import ImportScad, CustomObject, Cylinder, EPSILON
from ..geometry import Point, Vector, AnchorPoints

STEEL = [0.65, 0.67, 0.72]

# all dimensions are in mm: [hole_d, outer_d, heigh]
DIMENSIONS = {
    '603': [3,  9,  5],
    '604': [4, 12,  4],
    '605': [5, 14,  5],
    '606': [6, 17,  6],
    '607': [7, 19,  6],
    '608': [8, 22,  7],
    '609': [9, 24,  7],

    '623': [3, 10,  4],
    '624': [4, 13,  5],
    '625': [5, 16,  5],
    '626': [6, 19,  6],
    '627': [7, 22,  7],
    '628': [8, 24,  8],
    '629': [9, 26,  8],

    '633': [3, 13,  5],
    '634': [4, 16,  5],
    '635': [5, 19,  6],
    '636': [6, 22,  7],
    '637': [7, 26,  9],
    '638': [8, 28,  9],
    '639': [9, 30, 10],

    '673': [3,  6,  2.5],
    '674': [4,  7,  2.5],
    '675': [5,  8,  2.5],
    '676': [6, 10,  3],
    '677': [7, 11,  3],
    '678': [8, 12,  3.5],

    '683': [3,  7,  3],
    '684': [4,  9,  4],
    '685': [5, 11,  5],
    '686': [6, 13,  5],
    '687': [7, 14,  5],
    '688': [8, 16,  5],
    '689': [9, 17,  5],

    '693': [3,  8,  4],
    '694': [4, 11,  4],
    '695': [5, 13,  4],
    '696': [6, 15,  5],
    '697': [7, 17,  5],
    '698': [8, 19,  6],
    '699': [9, 20,  6],
}


class Bearing(CustomObject):

    def init_custom(self, model):
        hole_d, d, h = DIMENSIONS[model]
        self.hole_d = hole_d
        self.d = d
        self.h = h
        rim = 1.90 # this is correct for 608, I don't know the others
        self._outer = self.ring(d, d-rim, h).color(STEEL)
        self._seal = self.ring(d-rim, hole_d+rim, h*0.8).color('dodgerblue')
        self._inner = self.ring(hole_d+rim, hole_d, h).color(STEEL)
        self.anchors.copy_from(self._outer.anchors)

    def ring(self, outer_d, inner_d, h):
        result = Cylinder(d=outer_d, h=h)
        result -= Cylinder(d=inner_d, h=h+EPSILON)
        return result
