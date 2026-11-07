# Pokémon Sorter V1 — mechanical assembly

## Motion principle

Instead of picking up cards automatically (hard), the first machine has a horizontal, **face-up open-sided stage**. Operator places a single card on it. Camera records while the stage is level. A servo rotates the stage **around its long axis**, making the card slide **sideways** into the left or right collection bin. The stage returns to center for the next scan. No roller touches the front surface in this version.

### Dimensional design, all mm

| Dimension | Initial value | Reason / tolerance |
|---|---:|---|
| Pokémon card | 63 × 88 | Bare standard card; not sleeved |
| Scan tray outer size | 78 × 105 × 3 | 7.5 mm side clearance, 8.5 mm end clearance |
| Tray end stops | 1.2 high | Stop movement along the long axis while keeping side exits open |
| Printed trunnions | Ø6 | Rotate on printed pedestals; **print clearance** 0.55 diameter |
| Trunnion axis height above base | 70 | Keeps tray above 25 mm bins at 55-degree tilt |
| Sample servo center | 90° | Calibrate to mechanical level; not necessarily 90° on all brackets |
| Left/right sample angles | 35° / 145° | 55° from center each direction; reduce as needed |
| Two catch bins | 106 × 125 × 25 each | Print two, align adjacent under the tray |
| Camera standoff | adjustable ~120–200 above card | Determine actual distance from live preview to fit full card |
| Target overall footprint | approx 230 × 210 mm (including likely servo space, excluding camera support) | Excludes wiring and power adapters |

At 55° the tray's lower side drops ~32 mm below pivot height (half-width 39 mm × sin55°), leaving its lowest edge about 38 mm above the base, **higher than the 25 mm bin rims**. Safety margin is reduced by tolerances and card movement; verify by hand turning before power.

## Parts and print quantities

- `stl/tray.stl` ×1, PETG preferred, printed with support under the side-facing shafts and adapter disc. Print the scan surface **as smooth as possible** or lay on a removable smooth, non-abrasive insert.
- `stl/stand.stl` ×2, PETG, print upright on foot; use 4 mm hardware in foot slots.
- `stl/bin.stl` ×2, PLA or PETG; use soft bottom liner to protect corners.
- `stl/camera_plate.stl` ×1, PLA/PETG, generic 90 mm plate for a custom mast/adapter. It is **not a Raspberry Pi camera-specific mounting pattern**.
- Flat plywood/acrylic/printed composite base ~230 × 210 × 6–10.
- A camera mast (e.g. 2020 aluminum extrusion or custom printed upright) and an adjustable camera holder.
- MG90S metal-gear servo horn and custom-positioned **motor mount**, after measuring your servo. **No universal servo bracket is included**, because servo dimensions and horn patterns vary; the 2 × Ø2.2 mm pattern on the tray's 22 mm disc is a starting/drill guide only.
- M3/M4 bolts, washers, brackets, nuts as needed; cable clips and LED diffusors.

> **Important:** This CAD is a dimensioned proof-of-concept, not a production-tested fit. Run a dry mechanical assembly, check bearing fit, servo alignment, camera focus, and card behavior with duplicate/low-value cards. Use a metal spindle or bearing inserts if printed trunnions wear or crack.

## Print settings (starting points)

PETG, 0.2 mm layers, 0.4 mm nozzle, 4 walls, 30–40% infill, 5 top/bottom layers. Add supports under overhanging trunnions. Deburr/sand sharp edges *away from cards*; ensure no loose abrasive particles remain. Do not apply adhesive to any card-contacting surface.

## Assembly order

1. Print one tray and **one** stand; trial-fit Ø6 shaft into Ø6.55 bearing hole. Change `shaft_clearance` in OpenSCAD if too tight/loose.
2. Print the second stand; attach both to base so axial holes are **coaxial**. Leave several mm of axial play; there must be no binding.
3. Slide/mount tray between stands without servo. Rotate carefully ±55° by hand and verify it clears the bins.
4. Install two bins below tray, one each side of center line, aligned lengthwise. Add thin microfiber/soft foam landing surface.
5. Choose mount points for actual servo; ensure servo output shaft aligns with long axis. Use servo horn adapter and two small screws (or custom revised disc) **without lateral misalignment or coupling preload**.
6. Attach camera to independent adjustable mast; align lens perpendicular to level card. Fit whole card with margins; place two diffused lamps angled 30–45° to prevent glare.
7. Repeat 20 manual dry-run card releases to identify bounce, scratches, misroutes before electronics are powered.

## Version 2 — motorized hopper (future, not in these STL files)

Build a stack hopper at one end of the stage; a motorized **singulation roller + adjustable retard pad** pushes a single card onto the level tray. Important: card thickness (~0.3 mm) varies by stock and warping; gate clearance cannot be assumed from nominal thickness alone. Add one entry sensor, one exit sensor, transport timeout, double-feed detector, and automatic stop/reject logic. Keep the feeder detachable so V1 remains usable. Only automate after the tray-sorting accuracy and scan identification pass tests.

## Objective tests

- Scan stability: 50 cards, no visible image motion or exposure variation.
- Sorting: 100 inexpensive cards, target at least 98 placed in intended bin, **zero obvious edge/corner damage** before considering better cards.
- OCR/ID: build 100-card test set with confirmed IDs; record top-1 accuracy and review rate separately. No automatic routing of ambiguous scans.
- Hopper (later): 100-card run, record double-feeds, missed feeds and jams; must stop safely on any jam.
