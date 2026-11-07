# DIY Pokémon Card Sorter — Starter Build Pack (v0.1)

**This is a proof-of-concept, not a commercially tested card sorter.** It uses a manual feed, camera recognition + human confirmation, and one tilting tray servo. Designed to work from a Raspberry Pi with Linux + 40-pin header (Pi model must still be verified). All STLs were compiled from the provided OpenSCAD source and checked for watertight meshes; fit, travel and mechanical card safety have **not** been physically tested.

## What is included

```
README.md
cad/sorter_parts.scad       parametric mechanical source
stl/tray.stl                tilting capture tray (print 1)
stl/stand.stl               pivot support pedestal (print 2)
stl/bin.stl                 card catch tray (print 2)
stl/camera_plate.stl        adjustable mounting plate (print 1)
docs/MECHANICS.md           assembly, geometry, test requirements
docs/WIRING.md              electrical hookup, safety
docs/BOM.csv                suggested starter shopping list
docs/SOFTWARE_ARCHITECTURE.md  camera, OCR, catalog, API, state machine
diagrams/assembly.svg       schematic layout
diagrams/wiring.svg         electrical wiring schematic
software/app.py             FastAPI + OCR + TCGdex + mock/servo mode
software/requirements.txt
software/test_app.py
```

## First build

1. Print **only** `tray.stl` and **one** `stand.stl` first. Test shaft clearance without forcing the fit.
2. Print the other stand and both bins. Arrange on a 230×210 mm base; trial-fit tilt and output locations.
3. Independently mount a compatible camera ~120–200 mm above the stage; align perpendicular to the level card, using a live preview to choose exact height.
4. Set up the Pi and run `software/app.py` with `DRY_RUN=1`. Start with low-value Pokémon cards and an image upload.
5. Only then measure your servo shaft/horn and create a custom motor bracket. Install external motor PSU, PCA9685 and physical emergency-stop; verify motion by hand before powering motor.
6. Sort two groups with manually confirmed match and bin. Keep a `REVIEW` workflow for ambiguous or unrecognized cards.

## Mechanical note

The supplied STLs cover the tray, pedestals, bins and generic camera plate. **Servo mount and camera-PCB adapter are deliberately not final** because the specific servo dimensions, horn and actual Pi/camera model are unknown. A premature fixed bracket would likely not fit. Original OpenSCAD is parametric and editable after measuring real parts.

## Electrical note

Never wire servo power into Pi 3.3V GPIO, never supply 5V into Pi GPIO input, and do not feed servos from Pi 5V power. Use a separate motor supply with common ground. See `docs/WIRING.md`.

## Software note

`app.py` prioritizes avoiding mis-sorts over pretending to have high-confidence card identification. The OCR and image-candidate score are **suggestions, not certainties**. Operator must visually confirm the exact printing. Foil/reverse, prices and condition are outside V1 scope. TCGdex requires internet connectivity unless you later build the local cache.
