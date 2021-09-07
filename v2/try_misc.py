#!/usr/bin/python3

import os
from pyscad import Cube, Cylinder, Sphere, bolt_hole, Point, Union
from pyscad import autorender

def main():
    a = Cube(10, 10, 10).color('red')
    b = Cube(5, 5, 5).color('green').move_to(left=a.right)
    c = Cube(5, 5, 5).color('cyan').move_to(right=a.left)
    cyl = Cylinder(h=10, r=3).move_to(bottom=a.top)
    sph = Sphere(r=3).color('orange').move_to(bottom=cyl.top)
    p1 = Sphere(d=1).move_to(center=a.pmin)
    p2 = Sphere(d=1).move_to(center=a.pmax)
    return Union(a, b, c, cyl, sph, p1, p2)


if __name__ == '__main__':
    main().autorender()
