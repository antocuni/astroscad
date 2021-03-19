use <MCAD/2Dshapes.scad>

// THRUST BEARING f8-16m

// NOTE: this file does NOT model the bearing in all details. I only modeled
// the minumum I needed to make slots where to comfortably put the whashers

// according to the datasheets online, these bearing should have two different
// washers: one which is driven bt the outer diameter (so exactly 16mm) and
// the other driven by the bore diameter (so exatly 8mm).  However, the cheap
// ones which I have seems to have all washers of the same kind (16mm outer
// diameter, 8.2mm bore diameter).
// https://www.amazon.it/gp/product/B075F76KHN

OUTER_D = 16;
BORE_D = 8.2;
TOTAL_H = 5;
WASHER_H = 1.35;
BALL_CAGE_H = TOTAL_H - (WASHER_H*2);

module thrust_bearing_washer(tolerance=0.4) {
    inner_r = BORE_D / 2;
    outer_r = OUTER_D / 2;
    linear_extrude(WASHER_H) donutSlice(inner_r-(tolerance), outer_r+(tolerance), 0, 360);
}

module thrust_bearing_ball_cage() {
    inner_r = BORE_D / 2;
    outer_r = (OUTER_D * 0.9) / 2;
    linear_extrude(BALL_CAGE_H) donutSlice(inner_r, outer_r, 0, 360);
}

module thrust_bearing() {
    ball_h = TOTAL_H - (WASHER_H*2);
    color("grey") thrust_bearing_washer(tolerance=0);
    color("gold") translate([0, 0, WASHER_H]) thrust_bearing_ball_cage();
    color("grey") translate([0, 0, WASHER_H+BALL_CAGE_H]) thrust_bearing_washer();
}

module test_thrust_bearing_washer_slot() {
    H=4;
    difference() {
        cylinder(h=H, d=OUTER_D+4);
        translate([0, 0, -0.00001]) thrust_bearing_washer();
        translate([0, 0, H - WASHER_H +0.0001]) thrust_bearing_washer();
    }
}

//test_thrust_bearing_washer_slot();
thrust_bearing();
