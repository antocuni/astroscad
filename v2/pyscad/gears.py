from .scad import ImportScad

_gears = ImportScad('vendored/gears/gears.scad')


class WormFactory:
    modul = 1
    thread_starts = 2
    pressure_angle = 28
    lead_angle = 10

    @classmethod
    def spur(cls, teeth, height, bore_d=0, optimized=True):
        return _gears.worm_gear(
            tooth_number = teeth,
            width = height,
            gear_bore = bore_d,
            optimized = optimized,
            #
            thread_starts = cls.thread_starts,
            modul = cls.modul,
            pressure_angle = cls.pressure_angle,
            lead_angle = cls.lead_angle,
            #
            show_spur = True,
            show_worm = False
        )

    @classmethod
    def worm(cls, *, width, bore_d):
        return _gears.worm_gear(
            length = width,
            worm_bore = bore_d,
            #
            thread_starts = cls.thread_starts,
            modul = cls.modul,
            pressure_angle = cls.pressure_angle,
            lead_angle = cls.lead_angle,
            #
            tooth_number = 0,
            together_built = True,
            show_spur = False,
            show_worm = True
        )
