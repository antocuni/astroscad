#!./autoscad.py

import os
from solid import import_scad, union
import scad
from scad import Cube, cylinder, bolt_hole

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])

def main():
    return Cube(10, 20, 5, center='xy')
    #return cylinder(d=5, h=10)


if __name__ == '__main__':
    scad.render_to_file(main(), '/tmp/test_boundingbox.scad', fa=1, fs=0.4)
