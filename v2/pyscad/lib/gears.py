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
    def spur(cls, teeth, h, bore_d=0, optimized=True, *, axis='z', fast_rendering=False):
        return SpurGear(cls.module,
                        teeth,
                        h,
                        bore_d,
                        cls.pressure_angle,
                        -cls.lead_angle,
                        optimized,
                        axis=axis,
                        fast_rendering=fast_rendering)

    @classmethod
    def worm(cls, *, h, bore_d, axis='z', fast_rendering=False):
        return WormGear(cls.module,
                        cls.thread_starts,
                        h,
                        bore_d,
                        cls.pressure_angle,
                        cls.lead_angle,
                        axis=axis,
                        fast_rendering=fast_rendering)


class SpurGear(PySCADObject):
    """
    Spur gear centered in the origin.

    Same anchor points and properties of a cylinder.
    """

    def init_solid(self, module, teeth, h, bore_d, pressure_angle,
                   lead_angle, optimized, *, axis='z', fast_rendering=False):
        self.teeth = teeth
        self.h = h
        self.d = module * teeth
        self.r = r = self.d / 2

        # the addendum circle is the circle which circumscribes the tip of the
        # teeth
        addendum = 1 * module
        self.ar = self.r + addendum
        self.ad = self.d + addendum
        #
        #
        # to compute the anchors, we create a thrown-away Cylinder which is
        # "equivalent" to the spur
        cyl = Cylinder(d=self.d, h=h, axis=axis)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        if fast_rendering:
            self.solid = cyl.solid
            return
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

    def init_solid(self, module, thread_starts, h, bore_d,
                   pressure_angle, lead_angle, *, axis='z', fast_rendering=False):
        self.thread_starts = thread_starts
        self.r = r = module * thread_starts / (2 * sin(lead_angle))
        self.d = r*2
        self.h = h
        # to compute the anchors, we create a thrown-away Cylinder which is
        # "equivalent" to the worm
        cyl = Cylinder(d=self.d, h=h, axis=axis)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        if fast_rendering:
            self.solid = cyl.solid
            return

        # 1) create the worm
        width = h # gears.scad naming convention
        _worm = _gears.worm(module, thread_starts, width, bore_d, pressure_angle,
                            lead_angle, together_built=True)

        # 2) center on the Z axis
        _worm.translate(z=-h/2)

        # 3) rotate around the Z axis to match the correponding rotation of
        #    SpurGear, copied&adapted from gears.scad
        _worm.rotate(z=180/thread_starts)

        # 4) rotate to match the equivalent cylinder
        _worm.rotate(*cyl.rot_vector)

        # _worm is a GenericSCADWrapper, manually unwrap it
        self.solid = _worm.solid


class HerringboneGear(PySCADObject):

    def init_solid(self, *, module, teeth, h, bore_d, pressure_angle, helix_angle,
                   optimized, axis='z', fast_rendering=False):

        self.d = module * teeth
        self.r = r = self.d / 2

        # to compute the anchors, we create a thrown-away Cylinder which is
        # "equivalent" to the gear
        cyl = Cylinder(d=self.d, h=h, axis=axis)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        if fast_rendering:
            self.solid = cyl.solid
            return

        # create the gear and center on the Z axis
        _gear = _gears.spur_gear(module, teeth, h, bore_d, pressure_angle,
                                        helix_angle, optimized)
        _gear.translate(0, 0, -h/2)

        # rotate as needed by the 'axis', by re-using the rot_vector provided
        # by the equivalent cylinder
        _gear.rotate(*cyl.rot_vector)
        #
        # _gear is a GenericSCADWrapper, manually unwrap it
        self.solid = _gear.solid



class HerringboneRingGear(PySCADObject):

    def init_solid(self, *, module, teeth, h, rim_width, pressure_angle, helix_angle,
                   axis='z', fast_rendering=False):
        self.d = module * teeth  # XXX + rim_width?
        self.r = r = self.d / 2

        # to compute the anchors, we create a thrown-away Cylinder which is
        # "equivalent" to the gear
        cyl = Cylinder(d=self.d, h=h, axis=axis)
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        if fast_rendering:
            self.solid = cyl.solid
            return

        # create the gear and center on the Z axis
        _ring = _gears.ring_gear(module, teeth, h, rim_width,
                                             pressure_angle, helix_angle)
        _ring.translate(0, 0, -h/2)

        # rotate as needed by the 'axis', by re-using the rot_vector provided
        # by the equivalent cylinder
        _ring.rotate(*cyl.rot_vector)
        #
        # _gear is a GenericSCADWrapper, manually unwrap it
        self.solid = _ring.solid
