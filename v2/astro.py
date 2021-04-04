#!./autoscad.py

import os
from solid import import_scad, union, difference
import scad
from scad import cube, cylinder, in2mm, bolt_hole

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])
MCAD_bearing = import_scad('MCAD/bearing.scad')

class MyBearing:
    OUT_D = 22
    IN_D = 8
    H = 7

    def __new__(cls):
        return MCAD_bearing.bearing(model=608)

    @classmethod
    def inner_press_fit(cls, h, **kwargs):
        cyl = cylinder(h=h, d=cls.IN_D, **kwargs)
        return cyl

    @classmethod
    def adapter(cls, hole_d):
        h = cls.H + 1
        obj = cls.inner_press_fit(h)
        obj -= bolt_hole(d=hole_d, h=h)
        return obj

    @classmethod
    def slot(cls):
        return difference()(
            cylinder(d=cls.OUT_D+3, h=cls.H+3),
            cylinder(d=cls.OUT_D+0.1, h=cls.H+3).translate(z=3),
            cylinder(d=17, h=cls.H+2).translate(z=-1),
            )

def main():
    obj = union()
    obj += MyBearing()
    obj += MyBearing.adapter(hole_d = in2mm(1/4))


if __name__ == '__main__':
    scad.render_to_file(main(), 'astro.scad', fa=1, fs=0.4)
