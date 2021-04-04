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



def bracket():
    r_worm = 5.75877
    r_gear = 12
    t = 4 # thickness*2
    w = 28
    h = 2.5
    obj = cube(w+t, w+t,  h+t, center='xyz')
    obj -= cube(w+t+1, w, 2.5, center='xyz')
    obj -= cube(w+t+1, w, h+t+1, center='yz')
    #
    delta=-w/4
    obj -= bolt_hole(d=3.2, h=h+t, center=True).translate(x=delta)
    obj -= bolt_hole(d=3.2, h=50, center=True).rotate(x=90).translate(delta+r_gear+r_worm)
    return obj

def gear():
    return gears.spur_gear(1, 24, 2, pressure_angle=20, helix_angle=0).translate(z=-1)

root = union()
root += bracket()

if __name__ == '__main__':
    scad.render_to_file(root, 'test_gear.scad', fa=1, fs=0.4)
