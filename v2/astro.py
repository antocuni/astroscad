#!./autoscad.py

from solid import *


d = difference()(
    cube(10),
    sphere(15)
)

if __name__ == '__main__':
    scad_render_to_file(d, 'astro.scad')
