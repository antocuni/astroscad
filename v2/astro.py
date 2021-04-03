#!./autoscad.py

import os
from solid import import_scad, union
import scad
from scad import cube, cylinder, in2mm, bolt_hole

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/'
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



#obj = scad.cylinder(r1=10, r2=3, h=10, segments=60)
#obj+= scad.cylinder(r1=10, r2=3, h=-10, segments=60).color('red')

root = union()
#root += MyBearing()

def bearing_adapter():
    h = MyBearing.H + 1
    obj = MyBearing.inner_press_fit(h)
    obj -= bolt_hole(d=in2mm(1/4), h=h)
    return obj


root += bearing_adapter()




if __name__ == '__main__':
    scad.render_to_file(root, 'astro.scad', fa=1, fs=0.4)
