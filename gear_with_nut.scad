use <MCAD/2Dshapes.scad>
use <MCAD/nuts_and_bolts.scad>;
include <MCAD/units.scad>;
use <gears/gears.scad> // https://github.com/chrisspen/gears
use <thrust_bearing.scad>

$fa = 1;
$fs = 0.4;

WASHER_H = thrust_bearing_washer_h();

// params for lego-compatible wheels are taken from here:
// https://github.com/miklasiu/lego_gears/
module gear_with_nut(NUT_D=M5, TEETH=24, H=8, NUT_H=3.85) {
    difference() {
        translate([0, 0, -H/2]) spur_gear(1, TEETH, H, 0, pressure_angle=20, helix_angle=0, optimized=false);

        translate([0, 0, -H/2 - 0.0001])
            thrust_bearing_washer();

        translate([0, 0, H/2 - WASHER_H + 0.0001])
            thrust_bearing_washer();

        translate([0, 0, -NUT_H/2])
            nutHole(NUT_D, tolerance=0.1);

        translate([0, 0, -H/2 - 0.001])
            cylinder(H+0.002, d=7);
    }
}

gear_with_nut();
