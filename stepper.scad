use <v2/pyscad/vendored/gears/gears.scad> // https://github.com/chrisspen/gears
include <contrib/StepMotor_28BYJ-48.scad>
use <thrust_bearing.scad>

$fn=60;

TEETH = 24;

function stepper_gear_teeth() = TEETH;
function stepper_shaft_boss_d() = SBD;
function stepper_to_shaft_distance() = SHH - SHHF;

module stepper() {
    // like StepMotor28BYJ(), but positioned such that:
    //    1) the shaft is centered and pointing up
    //    2) the top surface lies on the XY plane
    //    3) the shaft points up
    translate([SBO, 0, -SHH+MBFH/2]) // (1+2)
    rotate([0, 180, 0])    // (3)
    union() {
        StepMotor28BYJ();
        // 5 colored hookup wires
        translate([0,0,-(MBH/2 - WRO)]) rotate([0,-90,0])
            wires();
    }
}

module stepper_gear_with_shaft(H, H_SHAFT) {
    tbwh = thrust_bearing_washer_h();
    shaft_d = SBD - 2;
    difference() {
        translate([0, 0, -H/2])
            spur_gear(1, TEETH, H, 0, pressure_angle=20, helix_angle=0, optimized=false);
        if (!$preview)
            translate([0, 0, -H/2-0.001]) thrust_bearing_washer();
    }
    difference() {
        translate([0, 0, -H_SHAFT-H/2 + 0.001]) cylinder(d=shaft_d, h=H_SHAFT);
        translate([0, 0, -H_SHAFT-H/2]) BYJ48_Hole(H_SHAFT+1);
    }
}

// this is intended to be used inside a difference() block
module stepper_mounting_holes(h=10, tolerance=0) {
    d = 4+tolerance;
    translate([SBO, -MHCC/2, -0.001]) cylinder(d=d, h=h+0.002);
    translate([SBO,  MHCC/2, -0.001]) cylinder(d=d, h=h+0.002);
}

// copied & adapted from https://www.thingiverse.com/thing:3047726 by Dries
// Pruimboom
module BYJ48_Hole(h=10)
{
    margin1=0.2;
    margin2=0.2;
    difference()
    {
       cylinder(d=SHD+margin1,h=h);
       translate([-3,1.5+margin2,-0.1])cube([6,6,h+1]);
       translate([-3,-1.5-margin2-6,-0.1])cube([6,6,h+1]);
    }
}



//stepper();
stepper_gear_with_shaft(H=4, H_SHAFT=5); // DON'T PRINT FROM THIS FILE! Print from astro.scad, which has the correct height
//stepper_mounting_holes();
