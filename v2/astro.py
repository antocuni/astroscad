#!./autoscad.py

from solid import *
import scad

obj = scad.cylinder(r1=10, r2=3, h=10, segments=60)
obj+= scad.cylinder(r1=10, r2=3, h=-10, segments=60).color('red')



if __name__ == '__main__':
    scad_render_to_file(obj, 'astro.scad')
