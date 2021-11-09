from ..scad import Cylinder, EPS

def ring(outer_d, inner_d, h):
    result = Cylinder(d=outer_d, h=h)
    result -= Cylinder(d=inner_d, h=h+EPS)
    return result
