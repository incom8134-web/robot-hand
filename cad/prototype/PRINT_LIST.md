# Print list — HAEBOT Hand prototype (EMAX ES08MA II)

Everything is in this folder. Print top to bottom. `xN` in a file name = print N copies.
Material: PLA is fine for all parts (PETG also OK). 0.4 mm nozzle, layer 0.2 mm (0.25 max).
Official InMoov parts (04–08) use InMoov's settings: 30 % infill, 2 mm walls. Our parts are small and get more walls.

| # | File | Qty | Infill | Walls | Supports | Orientation on the bed | Note |
|---|---|---|---|---|---|---|---|
| 01 | `01_FitTest_ServoSeat.stl` | 1 | 30 % | 3 | no | as exported (flat, open top up) | ~10 min. **Print first**, test one servo (guide step 2) |
| 02 | `02_ServoAdapter_ES08MA-II_x5.stl` | 5 | 40 % | 4 | no | as exported (arrow face up) | One per finger servo |
| 03 | `03_Pulley_ES08MA-II_x5.stl` | 5 | 100 % | — | no | as exported (flat top on the bed, horn pocket up) | |
| 04 | `04_WristLarge_official.stl` | 1 | 30 % | 2 mm | no | as exported | **You already printed this — reuse it.** |
| 05 | `05_Fingers_official_plate.stl` | 1 plate | 30 % | 2 mm | no | as exported | Finger segments |
| 06 | `06_FingerTips_official_plate.stl` | 1 plate | 30 % | 2 mm | **yes** | as exported | 5 tips |
| 07 | `07_FingerCover_official.stl` | 1 | 30 % | 2 mm | **yes** | as exported | |
| 08 | `08_PalmCover_official.stl` | 1 | 30 % | 2 mm | **yes** | as exported | Palm-side shell |
| 09 | `09_HandCover_JinieLogo.stl` | 1 | 30 % | 2 mm | **yes** | as exported | Back-of-hand shell with the Jinie EduTech logo (replaces the official HandCover) |
| 10 | `10_DeskStand.stl` | 1 | 25 % | 3 | no | as exported (base on the bed) | Holds the hand upright for testing |

STEP files (`01`, `02`, `03`, `10`) are clean CAD solids for Fusion 360 / FreeCAD. The official parts (04–09) exist only as meshes, so STL only.
If official parts fit too tight, set slicer "horizontal expansion" to about −0.15 for 05–08.

Not needed for the prototype (kept in `../original/`): official `i2_PulleyX5V1` (wrong spline), `i2_FingersMoldX5V3` (no sensors),
`i2_WristGearV1` (needs the InMoov forearm), `i2_HandCoverV1` (replaced by 09), the PDI6225 covers and `i2_Adapter1109MG`.
