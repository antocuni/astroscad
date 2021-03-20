use <gears/gears.scad> // https://github.com/chrisspen/gears
include <contrib/StepMotor_28BYJ-48.scad>

TEETH = 24;

function stepper_gear_teeth() = TEETH;
function stepper_shaft_boss_d() = SBD;

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

module stepper_gear() {
    H = 4;
    translate([0, 0, -H/2]) spur_gear(1, TEETH, H, 0, pressure_angle=20, helix_angle=0, optimized=false);
}

stepper();
//stepper_gear();
