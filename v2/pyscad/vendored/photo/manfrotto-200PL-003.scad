$fa=5; // default minimum facet angle is now 0.5°
$fs=0.5; // default minimum facet size is now 0.5 mm

//top plate
tpx = 52.6;
tpy = 47.6-5.2;
tpz = 6.3-1.5;

//base plate;
bpx = tpx;
bpy = tpy-5.2;// 42.4;
bpz = 9.85;

//front lip
flx = 42.95;
fly = 4.2;
flz = 5.1;
fd = 3.1;
flo = 2.4;

//back lip
blx = tpx;
bly = 16.7;
blz = bpz - tpz;

//backlip diameter
bd = 4;

//back lip z offset from top
blo = 2.4;

*union()
{
  cube([tpx,tpy,tpz]);
  translate([0,-(bpy-tpy)/2,0])
  cube([bpx,bpy,bpz]);
}

difference()
{
  translate([0,tpy-((tpy-bpy)/2)-fd/2,bpz])
    rotate([180,0,0])
      plate();
  
  translate([0,-1,0])
  {
    translate([bpx/2,bpy/2,0])
      r_screwhole();

    translate([bpx/2-15,bpy/2-10,0]) r_screwhole();
    translate([bpx/2-15,bpy/2+10,0]) r_screwhole();
    translate([bpx/2+15,bpy/2+10,0]) r_screwhole();
    translate([bpx/2+15,bpy/2-10,0]) r_screwhole();
  }
}

module plate()
{
  translate([0,(tpy-bpy)/2+bd/2,bpz-tpz])
    cube([bpx,bpy-fd/2-bd/2,tpz]);

  translate([0,bd/2,0])
    cube([fd,bly-fd/2,6]);

  translate([tpx-fd,bd/2,0])
    cube([fd,bly-fd/2,6]);

  hull()
  {
    translate([0,bd/2,bd/2])
      rotate([0,90,0])
        cylinder(d=bd,h=blx);

    translate([0,(tpy-bpy)/2,bpz-blo-bd/2])
      cube([blx,bd/2,bd/2]);
  }

  hull()
  {
    translate([0,(tpy-bpy)/2,bpz-blo-bd/2])
      cube([blx,bd/2,bd/2]);

    translate([0,bd/2+(tpy-bpy)/2,bpz-bd/2])
      rotate([0,90,0])
        cylinder(d=bd,h=blx);
  }

  hull()
  {
    translate([(blx-flx)/2,tpy-fd/2,fd/2])
      rotate([0,90,0])
        cylinder(d=fd,h=flx);

    translate([(blx-flx)/2,tpy-fd-(tpy-bpy)/2,bpz-fd/2-flo])
      cube([flx,fd,bd/2]);  
  }

  hull()
  {
    translate([(blx-flx)/2,tpy-fd-(tpy-bpy)/2,bpz-fd/2-flo])
      cube([flx,fd,bd/2]);

    translate([(blx-flx)/2,tpy-fd/2-(tpy-bpy)/2,bpz-fd/2])
      rotate([0,90,0])
        cylinder(d=fd,h=flx);
  }
}

module r_screwhole()
{
  translate([0,0,tpz])
    rotate([180,0,0])
      screwhole(tpz);
}

module screwhole(wz,hz=3.5)
{
  M3 = 3.4;
  M3h = 6;
  
  cylinder(d=M3,h=wz+1);
  
  translate([0,0,-0.01])
    cylinder(d=M3h,h=hz);
}
