#!./autoscad.py

from solid import *
import scad

obj = scad.cube(10, 10, 10, center='xz')


if __name__ == '__main__':
    scad_render_to_file(obj, 'astro.scad')
