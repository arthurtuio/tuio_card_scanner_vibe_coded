// Pokemon TCG sorter V1 - parametric proof-of-concept printable parts.
// Units: mm. Parts are mechanical prototypes, NOT production-validated.
// Export with: openscad -o tray.stl -D 'part="tray"' sorter_parts.scad
// Other part names: stand, bin, camera_plate.
// Print tray flat, stands on their feet, bins bottom-down.
part = "tray"; // [tray,stand,bin,camera_plate]
$fn = 64;

card_w = 63;
card_l = 88;
tray_w = 78;
tray_l = 105;
tray_t = 3;
shaft_d = 6;
shaft_l = 18;
shaft_clearance = 0.55; // increase for tight printer

module tray() {
    union() {
        // Flat scanning stage: card placed face-up, side edges OPEN for tilt release.
        translate([-tray_w/2,-tray_l/2,0])
            cube([tray_w,tray_l,tray_t]);
        // End stops only: do not obstruct front-facing printed collector number.
        for(y=[-tray_l/2+3, tray_l/2-3])
          translate([-31,y,tray_t]) cube([62,1.6,1.2]);
        // Strong end lugs, centered on lengthwise tilt axis.
        for(side=[-1,1]) {
          translate([-12,side*(tray_l/2+2)-4, -0.4])
            cube([24,8,9]);
          // Horizontal trunnion. Axis Y, at z 3.6 mm.
          translate([0,side*(tray_l/2+shaft_l/2+4),3.6])
            rotate([90,0,0]) cylinder(d=shaft_d,h=shaft_l,center=true);
        }
        // Servo horn adapter disc at +Y: drill/customize to match actual servo horn.
        translate([0,tray_l/2+shaft_l+4,3.6])
          rotate([90,0,0])
            difference(){
              cylinder(d=22,h=3,center=true);
              for(x=[-7,7]) translate([x,0,0]) cylinder(d=2.2,h=5,center=true);
            }
    }
}

// Bearing pedestal: print TWO. Place each at the opposite tray end.
// Center of through-hole is 70 mm above foot; clears 25-mm bin rims at 55° tilt.
module stand() {
    difference() {
      union() {
        translate([-25,-13,0]) cube([50,26,5]);
        translate([-13,-6,5]) cube([26,12,72]);
        // side ribs stiffen the upright
        for(x=[-13,11]) translate([x,-6,5]) cube([2,12,51]);
      }
      // 6.55 mm smooth rotational bore, oriented along Y
      translate([0,0,70]) rotate([90,0,0]) cylinder(d=shaft_d+shaft_clearance,h=18,center=true);
      // Mounting holes for M4 into wooden/acrylic base
      for(x=[-18,18]) translate([x,0,-0.5]) cylinder(d=4.3,h=6);
    }
}

// Print two, each as a soft-lined collection bin. Set on either side of tilt axis.
module bin() {
    bw=106; bl=125; bh=25; wall=2.4;
    difference() {
      translate([-bw/2,-bl/2,0]) cube([bw,bl,bh]);
      translate([-bw/2+wall,-bl/2+wall,2.6])
          cube([bw-2*wall,bl-2*wall,bh]);
    }
}

// Universal camera support plate to fasten to wood/2020 aluminum extrusion;
// mount actual camera PCB with adjustable adhesive-free adapter or printed spacer.
module camera_plate() {
    difference(){
      translate([-45,-15,0]) cube([90,30,4]);
      for(x=[-32,32]) hull(){
         translate([x,-7,-1]) cylinder(d=3.5,h=6);
         translate([x,7,-1]) cylinder(d=3.5,h=6);
      }
      // center access hole for the lens, size depends on camera casing
      translate([0,0,-1]) cylinder(d=12,h=6);
    }
}

if (part=="tray") tray();
else if (part=="stand") stand();
else if (part=="bin") bin();
else if (part=="camera_plate") camera_plate();
