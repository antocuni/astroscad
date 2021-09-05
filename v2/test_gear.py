#!./pyscad/autorender.py

import os
from pyscad import Cube, Cylinder, ImportScad, bolt_hole

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])
MCAD_bearing = ImportScad('MCAD/bearing.scad')
gears = ImportScad('gears/gears.scad')


R_WORM = 5.75877
def bracket():
    r_worm = R_WORM
    r_gear = 12
    t = 4 # thickness*2
    w = 28
    h = 2.5
    obj = Cube(w+t, w+t,  h+t, center='xyz')
    obj -= Cube(w+t+1, w, 2.5, center='xyz')
    obj -= Cube(w+t+1, w, h+t+1, center='yz')
    #
    delta = -w/4
    obj -= (
        bolt_hole(d=3.2, h=h+t, center=True)
        .tr(x=delta)
        )
    obj -= (
        bolt_hole(d=3.2, h=50, center=True)
        .rot(x=90)
        .tr(delta+r_gear+r_worm)
        )
    return obj.tr(x=-delta)

def worm_gear(spur, worm):
    h_gear = 2
    shaft_w = 3.2
    return gears.worm_gear(modul = 1,
                           tooth_number = 24,
                           thread_starts = 2,
                           width = h_gear,
                           length = 15,
                           worm_bore = 0,
                           gear_bore = shaft_w,
                           pressure_angle = 28,
                           lead_angle = 10,
                           optimized = 1,
                           together_built = True,
                           show_spur = spur,
                           show_worm = worm);

def main():
    root = bracket()
    root += worm_gear(spur=True, worm=False).translate(x=24/2)
    root += worm_gear(spur=False, worm=True).translate(x=24/2+R_WORM, y=15/2)

    #root -= cylinder(h=16, d=2.74, center=True, segments=6).m().rotate(x=90)
    #root -= cylinder(h=20, d=3.2, center=True).m()
    return root

if __name__ == '__main__':
    main().render_to_file()
