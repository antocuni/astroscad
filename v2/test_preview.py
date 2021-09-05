#!./pyscad/autorender.py

import os
from pyscad import Cube, Cylinder, Preview

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    '..',
])

class CubeOrCylinder(Preview):

    def preview(self):
        return Cube(10, 10, 10)

    def render(self):
        return Cylinder(d=10, h=10)


def main():
    return CubeOrCylinder()


if __name__ == '__main__':
    main().render_to_file()
