use <MCAD/2Dshapes.scad>
use <MCAD/regular_shapes.scad>
use <MCAD/boxes.scad>
use <MCAD/nuts_and_bolts.scad>
use <MCAD/polyholes.scad>
use <MCAD/bearing.scad>

$fa = 1;
$fs = 0.4;

/* Geometric conventions:

   - the rotation axis of the whole tracker is the Y axis

   - the upper plate stays above the XY plane (Z>0)

   - the lower plate stays below the XY plane (Z<0)
*/

VITAMINS = true && $preview; // whether to show the ball head, the bearings, etc.

TOL = 0.2;

// screw size
M5 = 5;
M8 = 8;
PH14 = 6.35;  // photographic 1/4" bolt ==> 6.35 mm
PH38 = 9.525; // photographic 3/8" bolt ==> 9.525 mm

// bearing model: 608RS (608zz should work as well)
BEARING_OUT_D = 22;
BEARING_IN_D = 12;
BEARING_THICKNESS = 7;
BEARING_WALL = 3; // the thickness of the wall to hold the bearing in place

// inner and outer hinge
HINGE_BOLT_L = 70;
HINGE_WALL_THICKNESS = 3;

OUT_HINGE_L = HINGE_BOLT_L - 6.40; // 6.40 is the tickness of the nut
OUT_HINGE_OUT_D = BEARING_OUT_D + 10;

IN_HINGE_L = OUT_HINGE_L - (HINGE_WALL_THICKNESS + BEARING_THICKNESS + TOL)*2;
IN_HINGE_OUT_D = 18;
IN_HINGE_IN_D = M8 + TOL;

// geometry of the tracker
LENGTH = 100;         // X axis
WIDTH = OUT_HINGE_L;  // Y axis
UPPER_THICKNESS = 10; // Z axis
LOWER_THICKNESS = OUT_HINGE_OUT_D/2;

R = 80.5;
THREADED_ROD_D = M5 + TOL*2;

BALL_D = 55; // ball head diameter
BALL_X = 40;

// VITAMINS

module PH38_bolt_head() {
    linear_extrude(6.15) hexagon(16.20/2);
}

module PH14_nut_hole(height) {
    d = 12.35+1.5;
    linear_extrude(height) circle(d=d, $fn=6);
}

module ball_head() {
    cylinder(d=BALL_D, h=90);
}

module threaded_rod() {
    color("grey")
        rotate([90, 80, 0])
        rotate_extrude(angle=90) translate([R, 0, 0]) circle(d=THREADED_ROD_D);
}

// ACTUAL MODEL

module upper_plate() {
    X = LENGTH;
    Y = WIDTH;
    Z = UPPER_THICKNESS;
    inner_hinge();
    difference() {
        color("#0DD", 0.8) // big upper plate
        translate([0, -Y/2, 0]) cube([LENGTH, Y, Z]);

        // remove a cylinder which is a bit bigger than the bearing slots, to
        // make sure that the upper plate does not touch them
        translate([0, OUT_HINGE_L/2, 0]) rotate([90, 0, 0])
        cylinder(d=OUT_HINGE_OUT_D+1, h=OUT_HINGE_L);

        // hole for the ball head
        translate([BALL_X, 0, -0.002]) polyhole(Z+0.004, PH38+TOL);

        // hole for the threaded rod
        threaded_rod();
    }
    if (VITAMINS) {
        color("grey") translate([BALL_X, 0, Z+0.0001]) ball_head();
        color("grey") translate([BALL_X, 0, -6.15]) PH38_bolt_head();
        threaded_rod();
    }
}

module inner_hinge() {
    Z = UPPER_THICKNESS;
    HL = IN_HINGE_L;
    HOD = IN_HINGE_OUT_D;
    HID = IN_HINGE_IN_D;
    difference() {
        union() {
            color("#055") // inner hinge
                rotate([90, 0, 0]) cylinder(d=HOD, h=HL, center=true);
            color("#088", 0.9) // small upper plate
                translate([0, -HL/2+0.5, -0.001]) cube([20, HL-1, Z-0.002]);
        }
        translate([0, HL/2+0.01, 0]) rotate([90, 0, 0]) polyhole(HL+0.02, HID);
    }
}

module bearing_slot(outer_d) {
    // the M8 nut has a diameter of ~14.5mm. We want the inner hole to be able
    // to contain it
    inner_r = 17 / 2;
    outer_r = outer_d/2;

    T = BEARING_THICKNESS;
    color("#00F")
    linear_extrude(BEARING_WALL) donutSlice(inner_r+TOL, outer_r, 0, 360);

    color("#55F")
    translate([0, 0, BEARING_WALL-0.0001]) linear_extrude(BEARING_THICKNESS + TOL)
        donutSlice(BEARING_OUT_D/2 + TOL, outer_r, 0, 360);
}

module lower_plate() {
    Z = LOWER_THICKNESS;
    HL = OUT_HINGE_L;
    HOD = OUT_HINGE_OUT_D;
    NUT_HOLE_H = 7.5;

    difference() {
        color("#0F0")
            union() {
            translate([0, -HL/2, -Z]) cube([LENGTH, HL, Z]);
            translate([0, HL/2, 0]) rotate([90, 0, 0]) cylinder(d=HOD, h=HL);
        }
        translate([0, 0, HOD/4]) cube([HOD+0.001, HL+0.001, HOD/2+0.001], center=true);
        translate([0, HL/2+0.1, 0]) rotate([90, 0, 0]) cylinder(d=BEARING_OUT_D+2, h=HL+0.2);

        // add a hole for the PH38_bolt_head
        translate([BALL_X, 0, -NUT_HOLE_H+0.001]) cylinder(d=PH38+10, h=NUT_HOLE_H);

        // add a hole for the threaded_rod
        threaded_rod();
    }

    // add the bearing slots
    translate([0,  HL/2, 0]) rotate([90, 0, 0]) bearing_slot(HOD, 16, 7, 3);
    translate([0, -HL/2, 0]) rotate([-90, 0, 0]) bearing_slot(HOD, 16, 7, 3);

    if (VITAMINS) {
        dist = HL/2 - BEARING_WALL;
        translate([0, dist, 0]) bearing(model=608, angle=[90, 0, 0]);
        translate([0, -dist, 0]) bearing(model=608, angle=[-90, 0, 0]);
    }
}

$t = 0.2;
rotate([0, -90*$t, 0]) upper_plate();
lower_plate();
