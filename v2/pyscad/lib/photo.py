import math
from ..scad import ImportScad, CustomObject, Cylinder
from ..geometry import Point, Vector, AnchorPoints

_manfrotto = ImportScad('vendored/photo/manfrotto-200PL-003.scad')


class Manfrotto_200PL(CustomObject):
    """
    """

    # these measures have been copied from the .scad files. I don't know
    # exactly why the total size of the plate is computed this way, but it
    # seems to work.

    # top plate
    _tpx = 52.6
    _tpy = 47.6-5.2
    _tpz = 6.3-1.5
    # base plate
    _bpx = _tpx
    _bpy = _tpy-5.2
    _bpz = 9.85

    sx = _bpx # size x
    sy = _tpy # size y (it's Tpy, not Bpy)
    sz = _bpz # size z

    def init_custom(self):
        self._plate = _manfrotto.plate()
        pmin = Point(0, 0, 0)
        pmax = Point(self.sx, self.sy, self.sz)
        self.anchors.set_bounding_box(pmin, pmax)
