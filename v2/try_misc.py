#!/usr/bin/python3

import os
from pyscad import Cube, Cylinder, bolt_hole, Point
from pyscad import autorender

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])

def main():
    O = Point(7, 7, 7)
    a = Cube(10, 10, 10).color('red').move_to(center=O)
    b = Cube(5, 5, 5).color('green').move_to(center=O, left=a.right)
    c = Cube(5, 5, 5).color('cyan').move_to(center=O, right=a.left)
    cyl = Cylinder(h=10, r=3).move_to(center=O, bottom=a.top)
    return a + b + c + cyl




if __name__ == '__main__':
    main().autorender()
