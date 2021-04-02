#!./autoscad.py

from solid import *
import scad

obj = scad.cube(10, 10, 30).translate(x=20).color('red', 0.4)



if __name__ == '__main__':
    scad_render_to_file(obj, 'astro.scad')
