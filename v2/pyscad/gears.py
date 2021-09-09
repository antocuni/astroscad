import math
from .scad import ImportScad

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
    def spur(cls, teeth, thickness, bore_d=0, optimized=True):
        # copied and adapted from gears.scad:worm_gear()
        module = cls.module
        thread_starts = cls.thread_starts
        pressure_angle = cls.pressure_angle
        lead_angle = cls.lead_angle
        width = thickness

        r_gear = module * teeth / 2
        # note: gears.scad uses pi*r_gear but I think it's a mistake because
        # it mixes degreen and radians
        gamma = -90 * width * sin(lead_angle) / (180 * r_gear)  # spur rotation angle
        spur = _gears.spur_gear(module, teeth, width, bore_d,
                                pressure_angle, -lead_angle, optimized);
        return spur.rotate(0, 0, gamma).translate(-r_gear, 0, -width/2)

    @classmethod
    def worm(cls, *, width, bore_d):
        # copied and adapted from gears.scad:worm_gear()
        module = cls.module
        thread_starts = cls.thread_starts
        pressure_angle = cls.pressure_angle
        lead_angle = cls.lead_angle
        pi = math.pi

        r_worm = module * thread_starts / (2 * sin(lead_angle))  # worm radius
        tooth_distance = module * pi/cos(lead_angle) # Tooth Spacing in Transverse Section
        x = 0.5 if thread_starts % 2 == 0 else 1


        worm = _gears.worm(module, thread_starts, width, bore_d, pressure_angle,
                           lead_angle, together_built=True)
        worm = worm.rotate(90, 180/thread_starts, 0)
        #worm = worm.translate([r_worm,(ceil(length/(2*tooth_distance))-x)*tooth_distance,0])
        return worm
