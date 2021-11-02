#!/usr/bin/python3

import os
from pyscad import autorender, Cube, Cylinder, ImportScad, bolt_hole, Union, Point
from pyscad.gears import WormFactory, _gears

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
])
MCAD_bearing = ImportScad('MCAD/bearing.scad')


R_WORM = 5.75877
def bracket():
    r_worm = R_WORM
    r_gear = 12
    t = 4 # thickness*2
    w = 28
    h = 2.5
    obj = Cube(w+t, w+t,  h+t)
    obj -= Cube(w+t+1, w, 2.5)
    obj -= Cube(w+t+1, w, h+t+1).translate((w+t+1)/2)
    #
    delta = -w/4
    obj -= (
        bolt_hole(d=3.2, h=h+t)
        .tr(x=delta)
        )
    obj -= (
        bolt_hole(d=3.2, h=50)
        .rot(x=90)
        .tr(delta+r_gear+r_worm)
        )
    return obj.tr(x=-delta)


def lego_gear():
    return _gears.spur_gear(modul=1,
                            tooth_number=24,
                            width=3,
                            bore=0,
                            pressure_angle=20,
                            helix_angle=0,
                            optimized=False).mod()


def main():
    root = Union()
    root += bracket()

    spur = WormFactory.spur(teeth=24, h=2, bore_d=3.2)
    worm = WormFactory.worm(length=15, bore_d=0)

    root += spur
    #root += worm.translate(x=spur.r+worm.r)
    root += worm.move_to(left=spur.right)

    #root -= cylinder(h=16, d=2.74, center=True, segments=6).m().rotate(x=90)
    #root -= cylinder(h=20, d=3.2, center=True).m()
    return root

def main2():
    tooth_number = 64
    r_gear = tooth_number/2

    root = Union()
    #root += lego_gear().translate(z=10)
    root += worm_gear(spur=True, worm=False, tooth_number=tooth_number).translate(x=r_gear)
    head = Cylinder(d=55, h=30).mod() # ball head
    head.move_to(bottom=Point.O).translate(z=2.1/2)
    root += head
    return root

def main3():
    root = Union()
    spur = WormFactory.spur(teeth=24, h=2, bore_d=3.2)
    #spur.show_bounding_box()
    root += spur
    root += Cylinder(r=spur.r, h=spur.h).mod()
    return root

def main4():
    root = Union()
    worm = WormFactory.worm(length=15, bore_d=0)
    worm.show_bounding_box()
    root += worm
    root += Cylinder(r=worm.r, h=worm.length).rot(x=90).mod()
    return root

if __name__ == '__main__':
    main().autorender()
    #main().render_to_image('/tmp/foo.png', size=(1024,1024))
