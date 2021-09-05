#!./autoscad.py

import os
from solid import import_scad, union
import scad
from scad import Cube, Cylinder, bolt_hole

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])

def main():
    #return Cube(10, 20, 5, center='xy')
    cyl = Cylinder(d1=5, d2=7, h=10)
    #cyl.translate(z=-5)
    #cyl.scale(z=2)
    #cyl.rotate(x=90, v=1)
    cyl.resize(x=10)
    #cyl.color('red')
    cyl
    cyl += Cube(10, 1, 1)
    cyl -= Cube(1, 1, 12).translate(z=-1)

    return cyl


if __name__ == '__main__':
    main().render_to_file()
