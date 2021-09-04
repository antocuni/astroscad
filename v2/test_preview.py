#!./autoscad.py

import os
import solid
from solid import import_scad, union
import scad
from scad import cube, cylinder, bolt_hole, Preview

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])

class CubeOrCylinder(Preview):

    def preview(self):
        return cube(10, 10, 10)

    def render(self):
        return cylinder(d=10, h=10)


def main():
    return CubeOrCylinder()


if __name__ == '__main__':
    scad.render_to_file(main(), '/tmp/test_preview.scad', fa=1, fs=0.4)
