#!/usr/bin/python3

import os
from pyscad import Cube, Cylinder, bolt_hole, Point
from pyscad import autorender

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])

def main():
    red = Cube(10, 10, 10, center='xyz').color('red')
    green = Cube(5, 5, 5, center='xyz').color('green')
    red.move_to(O=Point(20, None, None))
    green.move_to(bottom=red.top)
    return red+green



if __name__ == '__main__':
    main().autorender()
