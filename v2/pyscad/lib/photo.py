import math
from ..scad import ImportScad, CustomObject, Cylinder, Union
from ..geometry import Point, Vector, AnchorPoints

_manfrotto = ImportScad('vendored/photo/manfrotto-200PL-003.scad')


class Manfrotto_200PL(CustomObject):
    """
    Standard Manfrotto 200PL quick release plate.

    It defines the standard bounding box anchor points. However, the center of
    the object is set at the center of the top plate (because it's usually a
    more useful anchor point, e.g. if you need to put a hole in the middle of
    it).
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

    # front lip
    _flx = 42.95;
    _fly = 4.2;
    _flz = 5.1;
    _fd = 3.1;
    _flo = 2.4;

    # backlip diameter
    _bd = 4

    # totale size of the plate
    sx = _bpx # size x
    sy = _tpy # size y (it's Tpy, not Bpy)
    sz = _bpz # size z

    def init_custom(self, with_holes=False):
        self._obj = _manfrotto.plate()
        pmin = Point(0, 0, 0)
        pmax = Point(self.sx, self.sy, self.sz)
        # the center is computed later
        self.anchors.set_bounding_box(pmin, pmax, set_center=False)
        #
        # the actual top plate is defined by _manfrotto.plate(), but here we
        # insert a fake object so that we can attach anchor points to it. The
        # measures are taken directly from the scad file
        self.top_plate = Union()
        self.top_plate.anchors.set_bounding_box(
            Point.O,
            Point(self._bpx, self._bpy-self._fd/2-self._bd/2, self._tpz)
        )
        self.top_plate.translate(
            x=0,
            y=(self._tpy-self._bpy)/2 + self._bd/2,
            z=self._bpz-self._tpz
        )
        self.anchors.center = self.top_plate.center
        self.move_to(center=Point.O)

        # scren holes are arranged like a clock. The default manfrotto plate
        # has holes at 6, 9 and 12 hours, but we also compute the 3 for
        # completeness
        self.anchors.hole3  = Point(x =  14, y =   0, z=None)
        self.anchors.hole6  = Point(x =   0, y = -14, z=None)
        self.anchors.hole9  = Point(x = -14, y =   0, z=None)
        self.anchors.hole12 = Point(x =   0, y =  14, z=None)
        #
        if with_holes:
            self -= Cylinder(d=9.9, h=20).move_to(center=self.center)
            #self -= Cylinder(d=4.9, h=20).move_to(center=self.hole3)
            self -= Cylinder(d=4.9, h=20).move_to(center=self.hole6)
            self -= Cylinder(d=4.9, h=20).move_to(center=self.hole9)
            self -= Cylinder(d=4.9, h=20).move_to(center=self.hole12)
