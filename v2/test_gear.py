#!./autoscad.py

import os
from solid import import_scad, union
import scad
from scad import cube, cylinder, bolt_hole

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])
MCAD_bearing = import_scad('MCAD/bearing.scad')
gears = import_scad('gears/gears.scad')


R_WORM = 5.75877
def bracket():
    r_worm = R_WORM
    r_gear = 12
    t = 4 # thickness*2
    w = 28
    h = 2.5
    obj = cube(w+t, w+t,  h+t, center='xyz')
    obj -= cube(w+t+1, w, 2.5, center='xyz')
    obj -= cube(w+t+1, w, h+t+1, center='yz')
    #
    delta=-w/4
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

root = union()
root += bracket()
root += worm_gear(spur=True, worm=False).translate(x=24/2)
root += worm_gear(spur=False, worm=True).translate(x=24/2+R_WORM, y=15/2)

#root -= cylinder(h=16, d=2.74, center=True, segments=6).m().rotate(x=90)
#root -= cylinder(h=20, d=3.2, center=True).m()

#root += gears.planetary_gear(modul=0.5, sun_teeth=18, planet_teeth=24, number_planets=3, width=5, rim_width=3, bore=4, pressure_angle=20, helix_angle=30, together_built=True, optimized=True);


if __name__ == '__main__':
    scad.render_to_file(root, '/tmp/test_gear.scad', fa=1, fs=0.4)
