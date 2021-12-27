import math
from ..scad import ImportScad, PySCADObject, Cylinder
from ..geometry import Point, Vector, AnchorPoints

_gears = ImportScad('vendored/gears/gears.scad')


def sin(x):
    """
    sin(degrees)
    """
    return math.sin(math.radians(x))

def cos(x):
    """
    cos(degrees)
    """
    return math.cos(math.radians(x))

class WormFactory:
    module = 1
    thread_starts = 2
    pressure_angle = 28
    lead_angle = 10

    @classmethod
    def spur(cls, teeth, h, bore_d=0, optimized=True, *, axis='z'):
        return SpurGear(cls.module,
                        teeth,
                        h,
                        bore_d,
                        cls.pressure_angle,
                        -cls.lead_angle,
                        optimized,
                        axis=axis)

    @classmethod
    def worm(cls, *, length, bore_d):
        return WormGear(cls.module,
                        cls.thread_starts,
                        length,
                        bore_d,
                        cls.pressure_angle,
                        cls.lead_angle)


class SpurGear(PySCADObject):
    """
    Spur gear centered in the origin.

    Same anchor points and properties of a cylinder.
    """

    def init_solid(self, module, teeth, h, bore_d, pressure_angle,
                   lead_angle, optimized, *, axis='z'):
        self.h = h
        self.d = module * teeth
        self.r = r = self.d / 2
        #
        # to compute the anchors, we create a thrown-away Cylinder which is
        # "equivalent" to the spur
        cyl = Cylinder(d=self.d, h=h, axis=axis)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        #
        # create the spur and place it at center
        width = h # gears.scad naming convention
        _spur = _gears.spur_gear(module, teeth, width, bore_d, pressure_angle,
                                 lead_angle, optimized)
        _spur.translate(0, 0, -width/2)
        #
        # spur rotation angle, copied from gears.scad:worm_gear()
        # This is computed to match the corresponding rotation angle of the worm
        gamma = -90 * width * sin(-lead_angle) / (math.pi * r)
        _spur.rotate(0, 0, gamma)
        #
        # rotate as needed by the 'axis', by re-using the rot_vector provided
        # by the equivalent cylinder
        _spur.rotate(*cyl.rot_vector)
        #
        # _spur is a GenericSCADWrapper, manually unwrap it
        self.solid = _spur.solid

class WormGear(PySCADObject):

    def init_solid(self, module, thread_starts, length, bore_d,
                   pressure_angle, lead_angle):
        # compute anchors
        self.r = r = module * thread_starts / (2 * sin(lead_angle))
        self.length = length
        pmin = Point(-r, -length/2, -r)
        pmax = Point(+r, +length/2, +r)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(pmin, pmax)
        #
        # 1) create the worm
        width = length # gears.scad naming convention
        _worm = _gears.worm(module, thread_starts, width, bore_d, pressure_angle,
                            lead_angle, together_built=True)
        #
        # 2) rotate
        #     - the rotation around the X axis is to "lay it down" in a
        #       position which is by default compatible with SpurGear. This is
        #       also why it has a "length" instead of a "height"
        #
        #     - the rotation around the Y axis is to match the correponding
        #       rotation of SpurGear, copied from gears.scad
        _worm.rotate(90, 180/thread_starts, 0)
        #
        # 3) center on the Y axis
        _worm.translate(y=length/2)
        #
        # _worm is a GenericSCADWrapper, manually unwrap it
        self.solid = _worm.solid
