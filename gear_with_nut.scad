use <MCAD/2Dshapes.scad>
use <MCAD/nuts_and_bolts.scad>;
include <MCAD/units.scad>;
use <gears/gears.scad> // https://github.com/chrisspen/gears
use <thrust_bearing.scad>

$fa = 1;
$fs = 0.4;

WASHER_H = thrust_bearing_washer_h();
H = 8;
TEETH = 24;
NUT_H = 3.82;

function gear_with_nut_teeth() = TEETH;
function gear_with_nut_h() = H;

// params for lego-compatible wheels are taken from here:
// https://github.com/miklasiu/lego_gears/
module gear_with_nut(NUT_D=M5, NUT_H=NUT_H, force_holes=false) {
    difference() {
        translate([0, 0, -H/2]) spur_gear(1, TEETH, H, 0, pressure_angle=20, helix_angle=0, optimized=false);

        // in preview mode, the gear becomes a mess if I put these.
        if (!$preview || force_holes) {
            translate([0, 0, -H/2 - 0.0001])
                thrust_bearing_washer();

            translate([0, 0, H/2 - WASHER_H + 0.0001])
                thrust_bearing_washer();

            translate([0, 0, -NUT_H/2])
                my_nutHole(NUT_D, NUT_H);

            // see the comment inside thrust_bearing.scad for why we need d=6.2
            translate([0, 0, -H/2 - 0.001])
                cylinder(H+0.002, d=6.2);
        }
    }
}

// like nutHole, but allows to specify a custom thickness
module my_nutHole(size, thickness, tolerance=0.05)
{
    linear_extrude(thickness) nutHole(size, tolerance=tolerance, proj=1);
}

module test_my_nuthole() {
    H = 8;
    difference() {
        translate([0, 0, -H/2])         cylinder(d=12, H);
        translate([0, 0, -NUT_H/2])     my_nutHole(M5, NUT_H);
        translate([0, 0, -H/2 - 0.001]) cylinder(H+0.002, d=7);
    }
}

// cura pauseAtHeight: pause at layer JUST BEFORE the one which starts
// covering the nut (e.g. if the nut cover is done at layer 31, you need to
// pause at 30)
gear_with_nut(force_holes=true);
//test_my_nuthole();
