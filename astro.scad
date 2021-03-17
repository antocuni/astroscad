use <MCAD/2Dshapes.scad>
use <MCAD/regular_shapes.scad>
use <MCAD/boxes.scad>
use <MCAD/nuts_and_bolts.scad>
use <MCAD/polyholes.scad>

$fa = 1;
$fs = 0.4;


/* Geometric conventions:

   - the rotation axis of the whole tracker is the Y axis

   - the upper plate stays above the XY plane (Z>0)

   - the lower plate stays below the XY plane (Z<0)
*/

// screw size
M8 = 8;
PH14 = 6.35;  // photographic 1/4" screw ==> 6.35 mm
PH38 = 9.525; // photographic 3/8" screw ==> 9.525 mm

TOL = 0.2;

// geometry of the tracker
LENGTH = 100;         // X axis
WIDTH = 65;           // Y axis
UPPER_THICKNESS = 10; // Z axis
LOWER_THICKNESS = 10; // Z axis

BEARING_THICKNESS = 7;

HINGE_BOLT_L = 60;    // Y axis
HINGE_WALL_THICKNESS = 3;
HINGE_INNER_L = HINGE_BOLT_L - (HINGE_WALL_THICKNESS + BEARING_THICKNESS + TOL)*2;
HINGE_THICKNESS = 3;

BALL_D = 55; // ball head diameter
BALL_X = 25 + 5 + BALL_D/2; // ball head X coordinate

module upper_plate(ball_head=false) {
    X = LENGTH;
    Y = WIDTH;
    Z = UPPER_THICKNESS;

    HL = HINGE_INNER_L;
    H_out_d = M8 + HINGE_THICKNESS;
    H_in_d = M8 + TOL;

    // inner hinge
    difference() {
        union() {
            color("#F00")
                rotate([90, 0, 0]) cylinder(d=H_out_d, h=HL, center=true);
            color("#F55", 0.9)
                translate([-H_out_d/2, -HL/2, 0]) cube([25, HL, Z]);
        }
         translate([0, HL/2+0.01, 0]) rotate([90, 0, 0]) polyhole(HL+0.02, H_in_d);
    }

    // rest of the plate
    difference() {
        color("#F88")
            translate([25-H_out_d/2-0.01, -Y/2, 0]) cube([X-25, Y, Z]);
        // hole for the ball head
        translate([BALL_X, 0, -0.002]) polyhole(Z+0.004, PH38+TOL);
    }

    if (ball_head) {
        color("grey")
            translate([BALL_X, 0, Z+0.0001]) cylinder(d=BALL_D, h=5);

        color("grey")
            translate([BALL_X, 0, -6.15]) PH38_bolt_head();
    }
}

module PH38_bolt_head() {
    linear_extrude(6.15) hexagon(16.20/2);
}


rotate([0, -90*$t, 0]) upper_plate(ball_head=true);

