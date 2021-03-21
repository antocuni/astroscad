use <MCAD/2Dshapes.scad>
use <MCAD/regular_shapes.scad>
use <MCAD/boxes.scad>
use <MCAD/nuts_and_bolts.scad>
use <MCAD/polyholes.scad>
use <MCAD/bearing.scad>
use <gear_with_nut.scad>
use <thrust_bearing.scad>
use <contrib/screw_holes.scad>
use <stepper.scad>

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
M3 = 3;
M5 = 5;
M8 = 8;
PH14 = 6.35;  // photographic 1/4" bolt ==> 6.35 mm
PH38 = 9.525; // photographic 3/8" bolt ==> 9.525 mm

// the PH14 bolt fastens the quick-release plate to the lower plate. How long
// is the part which penetrates?
PH14_BOLT_LENGTH = 5;

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
UPPER_LENGTH = 130;   // X axis
LOWER_LENGTH = 130;
WIDTH = OUT_HINGE_L;  // Y axis
UPPER_THICKNESS = OUT_HINGE_OUT_D/2;; // Z axis
LOWER_THICKNESS = OUT_HINGE_OUT_D/2;

R = 80.5;
THREADED_ROD_D = M5;

BALL_D = 55; // ball head diameter
BALL_X = 33;

GEAR_CAVITY_X = BALL_X + 25;

GEAR_H = gear_with_nut_h();
DISTANCE_BETWEEN_GEARS = (gear_with_nut_teeth() + stepper_gear_teeth()) / 2;
STEPPER_X = R + DISTANCE_BETWEEN_GEARS;

GEAR_CAP_WIDTH = OUT_HINGE_L;
GEAR_CAP_LENGTH = thrust_bearing_outer_d() + 4;
GEAR_CAP_PLATE_THICKNESS = thrust_bearing_washer_h() + 2;
GEAR_CAP_PILLAR_H = GEAR_H + thrust_bearing_ball_cage_h()*2;
GEAR_CAP_PILLAR_DISTANCE = (OUT_HINGE_L/2) - 7;
GEAR_CAP_PILLAR_D = M3; // inner diameter of the screw
GEAR_CAP_TOTAL_H = GEAR_CAP_PLATE_THICKNESS + GEAR_CAP_PILLAR_H;

// bah, the screw_holes library uses a different convention for the global
// M3/M4/M5 etc variables, so we cannot use them directly :(. Thats' why we
// use<> instead of include<> it. Manually copy&paste the few things we need
SCREW_DIN965 = 1; // for screw_holes.scad
SCREW_M3 = 3;


// VITAMINS

module PH38_bolt_head() {
    linear_extrude(6.15) hexagon(16.20/2);
}

module PH14_nut_hole(height) {
    d = 12.35+1.5;
    linear_extrude(height) circle(d=d, $fn=6);
}

module PH14_bolt_hole(height) {
    polyhole(h, PH14+0.3);
}

module ball_head() {
    cylinder(d=BALL_D, h=90);
}

module threaded_rod(d=THREADED_ROD_D) {
    color("grey")
        rotate([90, 75, 0])
        rotate_extrude(angle=90) translate([R, 0, 0]) circle(d=d);
}

// ACTUAL MODEL

module upper_plate() {
    X = UPPER_LENGTH;
    Y = WIDTH;
    Z = UPPER_THICKNESS;
    inner_hinge();
    difference() {
        color("#0DD", 0.8) // big upper plate
        translate([0, -Y/2, 0]) cube([X, Y, Z]);

        // remove a cylinder which is a bit bigger than the bearing slots, to
        // make sure that the upper plate does not touch them
        translate([0, OUT_HINGE_L/2, 0]) rotate([90, 0, 0])
        cylinder(d=OUT_HINGE_OUT_D+1, h=OUT_HINGE_L);

        // hole for the ball head
        translate([BALL_X, 0, -0.002]) polyhole(Z+0.004, PH38+TOL);

        // my PH38 bolt is too short, make some more space for it
        translate([BALL_X, 0, -0.001]) cylinder(d=PH38+10, h=5);

        // hole for the threaded rod
        threaded_rod(d=THREADED_ROD_D+TOL*2);

        gear_cavity();
    }
    if (VITAMINS) {
        color("grey") translate([BALL_X, 0, Z+0.0001]) ball_head();
        color("grey") translate([BALL_X, 0, -6.15]) PH38_bolt_head();
        threaded_rod();
        color("grey") rotate([0, -7, 0]) translate([R, 0]) nutHole(M5);
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
    module notch() {
        l = (outer_r - inner_r);
        thick = 0.2;
        translate([inner_r, 0, 0]) cube([l, thick, thick]);
    }

    T = BEARING_THICKNESS;
    color("#00F")
    difference() {
        linear_extrude(BEARING_WALL) donutSlice(inner_r+TOL, outer_r, 0, 360);
        rotate([0, 0, 0]) notch();
        rotate([0, 0, -10]) notch();
        rotate([0, 0, -20]) notch();
    }

    color("#55F")
    translate([0, 0, BEARING_WALL-0.0001]) linear_extrude(BEARING_THICKNESS + TOL)
        donutSlice(BEARING_OUT_D/2 + TOL, outer_r, 0, 360);
}

module lower_plate() {
    tbwh = thrust_bearing_washer_h();
    tbbh = thrust_bearing_ball_cage_h();
    X = LOWER_LENGTH;
    Z = LOWER_THICKNESS;
    HL = OUT_HINGE_L;
    HOD = OUT_HINGE_OUT_D;
    NUT_HOLE_H = 7.5;
    PILLAR_Y = GEAR_CAP_PILLAR_DISTANCE;

    difference() {
        color("#0F0")
            union() {
            translate([0, -HL/2, -Z]) cube([X, HL, Z]);
            translate([0, HL/2, 0]) rotate([90, 0, 0]) cylinder(d=HOD, h=HL);
        }
        translate([0, 0, HOD/4]) cube([HOD+0.001, HL+0.001, HOD/2+0.001], center=true);
        translate([0, HL/2+0.1, 0]) rotate([90, 0, 0]) cylinder(d=BEARING_OUT_D+2, h=HL+0.2);

        // add a hole for the PH38_bolt_head
        translate([BALL_X, 0, -NUT_HOLE_H+0.001]) cylinder(d=PH38+10, h=NUT_HOLE_H);

        // add a hole for the threaded_rod, but bigger to make sure it can
        // pass without friction
        threaded_rod(d=THREADED_ROD_D + 3);

        // add a slot for the PH14 nut, and a hole for the PH14 bolt
        translate([16, 0, -Z+PH14_BOLT_LENGTH]) PH14_nut_hole(Z);
        translate([16, 0, -Z-1]) polyhole(Z+2, PH14+0.3);

        gear_cavity();

        // add holes for the pillar screws
        translate([R,  PILLAR_Y, -Z-0.001]) cylinder(d=M3+TOL, h=Z+0.002);
        translate([R, -PILLAR_Y, -Z-0.001]) cylinder(d=M3+TOL, h=Z+0.002);

        // and slots for the nuts. We put two of them one above the other
        // because nutHole does not let us to specify the height :(
        translate([R,  PILLAR_Y, -Z-0.001]) nutHole(M3, tolerance=TOL);
        translate([R,  PILLAR_Y, -Z+2.39]) nutHole(M3, tolerance=TOL);
        translate([R, -PILLAR_Y, -Z-0.001]) nutHole(M3, tolerance=TOL);
        translate([R, -PILLAR_Y, -Z+2.39]) nutHole(M3, tolerance=TOL);

        // add slots for the stepper hole and flanges
        sbd = stepper_shaft_boss_d();
        translate([STEPPER_X, 0, -Z-0.001]) stepper();
        translate([STEPPER_X, 0, -Z-0.001]) cylinder(d=sbd+TOL, h=Z+0.002);
        translate([STEPPER_X, 0, -Z]) stepper_mounting_holes(h=Z);
        // slot for the thrust bearing washer (for the stepper gear)
        translate([STEPPER_X, 0, -GEAR_H/2 - tbbh - tbwh + 0.001])
            thrust_bearing_washer();
    }

    // add the bearing slots
    translate([0,  HL/2, 0]) rotate([90, 0, 0]) bearing_slot(HOD, 16, 7, 3);
    translate([0, -HL/2, 0]) rotate([-90, 0, 0]) bearing_slot(HOD, 16, 7, 3);

    if (VITAMINS) {
        dist = HL/2 - BEARING_WALL;
        translate([0, dist, 0]) bearing(model=608, angle=[90, 0, 0]);
        translate([0, -dist, 0]) bearing(model=608, angle=[-90, 0, 0]);
        color("white") translate([R, 0, 0]) gear_with_nut();
        translate([R, 0, -GEAR_H/2 - tbwh - tbbh]) thrust_bearing();
        translate([R, 0, GEAR_H/2 - tbwh]) thrust_bearing();
        translate([STEPPER_X, 0, -Z]) stepper();
    }
}

module gear_cavity() {
    // this is meant to be used inside a difference() block: make enough room
    // for the gear and the thrust bearings, in both the lower and upper
    // plates.
    tbbh = thrust_bearing_ball_cage_h();
    tbwh = thrust_bearing_washer_h();
    H = GEAR_H + tbbh*2;
    Y = OUT_HINGE_L + 1;
    LENGTH = max(UPPER_LENGTH, LOWER_LENGTH);
    translate([GEAR_CAVITY_X , -Y/2, -H/2]) cube([LENGTH, Y, H]);
    // slot for the thrust bearing washer
    translate([R, 0, -GEAR_H/2 - tbbh - tbwh + 0.001]) thrust_bearing_washer();

    // space for the gear cap
    UZ = GEAR_H/2+tbbh;
    translate([GEAR_CAVITY_X, -Y/2, UZ-0.001])
        cube([UPPER_LENGTH, Y, GEAR_CAP_PLATE_THICKNESS + 0.001]);

    // space for the nut which keep the rod in place
    h=4.1;
    translate([R, 0, UZ+h-1]) cylinder(d=13, h=h);
}

module gear_cap() {
    tbbh = thrust_bearing_ball_cage_h();
    tbwh = thrust_bearing_washer_h();
    X = GEAR_CAP_LENGTH;
    Y = GEAR_CAP_WIDTH;
    Z = GEAR_CAP_PLATE_THICKNESS;

    PILLAR_Y = GEAR_CAP_PILLAR_DISTANCE;
    PILLAR_H = GEAR_CAP_PILLAR_H;
    PILLAR_ID = GEAR_CAP_PILLAR_D + TOL;

    module screw(y) {
        //h = $preview ? 0 : PILLAR_H + Z;
        h = PILLAR_H + Z;
        z = GEAR_H/2 + tbbh + Z;
        translate([R, y, z+0.001])
        rotate([0, 180, 0]) {
        screw_hole(SCREW_DIN965, SCREW_M3, h, h);
        // screw_hole make a very tight hole. Enlarge it a bit
        translate([0, 0, -0.001]) cylinder(d=PILLAR_ID, h=PILLAR_H+Z+0.003);
        }
    }
    module pillar() {
        W = PILLAR_ID+2;
        difference() {
            translate([-GEAR_CAP_LENGTH/2, -W/2, 0])
                cube([GEAR_CAP_LENGTH, W, PILLAR_H+0.001]);
        }
    }
    color("#55D", 0.7)
    difference() {
        union() {
            translate([R, 0, Z/2+GEAR_H/2+tbbh]) cube([X, Y, Z], center=true);
            translate([R,  PILLAR_Y, -PILLAR_H/2]) pillar();
            translate([R, -PILLAR_Y, -PILLAR_H/2]) pillar();
        }
        // slot for the thrust bearing washer
        translate([R, 0, GEAR_H/2 + tbbh - 0.001]) thrust_bearing_washer();

        // add holes for the two screws
        screw(PILLAR_Y);
        screw(-PILLAR_Y);

        // add a hole for the threaded_rod, but bigger to make sure it can
        // pass without friction
        threaded_rod(d=THREADED_ROD_D + 3);
    }
    echo("PILLAR: total length of the screw (including head) = ", PILLAR_H + Z + LOWER_THICKNESS);
}

module stepper_gear() {
    Z = LOWER_THICKNESS;
    gh = 4;
    ghs = Z - stepper_to_shaft_distance() - gh/2;
    color("white") translate([STEPPER_X, 0, 0]) stepper_gear_with_shaft(H=gh, H_SHAFT=ghs);
}

$t = 0.2;
rotate([0, -90*$t, 0]) upper_plate();
lower_plate();
gear_cap();
stepper_gear();
