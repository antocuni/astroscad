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
    cyl.translate(z=-5)
    #cyl.scale(z=2)
    #cyl.rotate(x=90, v=1)
    cyl.resize(x=20)
    #cyl.color('red')
    cyl.m()
    return cyl


if __name__ == '__main__':
    scad.render_to_file(main(), '/tmp/test_boundingbox.scad', fa=1, fs=0.4)
