#!./venv/bin/python3

import math
from pyscad import (Cube, Cylinder, Sphere, Point, Union, CustomObject, EPS,
                    TCone, Vector, PySCADObject)
from pyscad.shapes import DonutSlice
from pyscad.lib.misc import RoundHole, Washer
from pyscad.lib.bearing import Bearing
from pyscad.util import in2mm
import astro
from astro import main, check_almost_equal

def dsub_connector():
    # this is the male connector
    dsub = CustomObject()
    flange = Cube(1.2, 30.8, 12.5)
    dsub.flange = flange
    dsub.inside = Cube(8.45+4, 19.3, 10.75).move_to(left=flange.right)
    dsub.outside = Cube(5.9, 18.1, 9.45).move_to(right=flange.left)
    dist = (28.7-3)/2 # distance between the center of the hole and the center of the flange
    dsub -= Cylinder(d=3, h=10, axis='x').move_to(center=flange.center).tr(y=dist)
    dsub -= Cylinder(d=3, h=10, axis='x').move_to(center=flange.center).tr(y=-dist)
    dsub.anchors.flange_right = flange.right
    dsub.anchors.flange_left = flange.left
    dsub.anchors.flange_front = flange.front
    dsub.anchors.flange_back = flange.back
    dsub.anchors.flange_bottom = flange.bottom
    return dsub

def board():
    res = CustomObject()
    base = Cube(102, 88, 1.6).color('tan')
    res.base = base

    buttons = Cube(59, 13, 12.6).color('red')
    buttons.move_to(bottom=base.top, back=base.front+21, right=base.right-3.36)
    res.buttons = buttons

    mcu = Cube(58, 22.6, 20.4).color('blue')
    mcu.move_to(bottom=base.top, front=base.front+24.65, right=base.right-6.71)
    res.mcu = mcu

    buzzer = Cylinder(d=15.2, h=3.7).color('black')
    res.buzzer = buzzer.move_to(bottom=base.top, back=base.back-4.6, right=base.right-8.46)

    terminals = Cube(10.15, 44, 14.35).color('green')
    terminals.move_to(bottom=base.top, left=base.left, front=base.front+20.75)
    res.terminals = terminals

    capacitor = Cylinder(d=18.2, h=32.3, axis='x').color('darkblue')
    capacitor.move_to(bottom=base.top, right=base.right-24, front=base.back-27.3)
    res.capacitor = capacitor

    capacitor2 = Cylinder(d=8.2, h=14.4).color('darkblue')
    res.capacitor2 = capacitor2.move_to(bottom=base.top, front=base.front+6.7, left=base.left+12.8)

    booster = Cube(43, 21.3, 12.8).color('blue')
    res.booster = booster.move_to(bottom=base.top, back=base.back, left=base.left)

    transistor = Cylinder(d=5, h=8).color('grey')
    res.transistor = transistor.move_to(bottom=base.top, right=base.right-4.75, front=base.back-26.78)

    screw_hole = RoundHole(d=3.75, h=25)
    res -= screw_hole.move_to(front=base.front+16.6, left=base.left+3)

    screw_hole2 = RoundHole(d=3.75, h=25)
    res -= screw_hole2.move_to(back=base.back-31, right=base.right-12.5)

    usb_pcb = Cube(18, 30, 2)
    usb_pcb.move_to(right=base.left - 3, back=base.back - 5)
    usb_pcb.move_to(bottom=base.top + 3)
    res.usb_pcb = usb_pcb

    usb = Cube(16, 12, 12)
    usb.move_to(center=usb_pcb.center)
    usb.move_to(right=usb_pcb.right -6)
    usb.move_to(bottom=usb_pcb.top)
    res.usb = usb

    dsub = dsub_connector()
    dsub.move_to(flange_left=usb_pcb.left, flange_front=base.front, flange_bottom=base.bottom)
    dsub.tr(z=5)
    res.dsub = dsub

    return res

def build():
    global FAST_RENDERING, VITAMINS
    FAST_RENDERING = astro.FAST_RENDERING
    VITAMINS = astro.VITAMINS
    obj = CustomObject()

    obj.board = board()

    return obj


if __name__ == '__main__':
    main(build)
