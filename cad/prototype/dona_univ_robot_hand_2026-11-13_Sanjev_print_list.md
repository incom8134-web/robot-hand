# Print list — HAEBOT Hand prototype (EMAX ES08MA II)

> **Superseded in part on 2026-11-16.** The finger servos moved to **5 x Feetech STS3215 (12 V) in the forearm**, so the ES08MA II parts **01, 02 and 03** (fit-test seat, servo adapter, pulley) no longer apply. The official hand parts **04 to 09** and the desk stand **10** are unchanged and still correct to print. The forearm bed and pulleys for the STS3215 are not designed yet — see [`../../electronics/version_2/dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md`](../../electronics/version_2/dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md).

Everything is in this folder. Print top to bottom. `xN` in a file name = print N copies.
Material: PLA is fine for all parts (PETG also OK). 0.4 mm nozzle, layer 0.2 mm (0.25 max).
Official InMoov parts (04–08) use InMoov's settings: 30 % infill, 2 mm walls. Our parts are small and get more walls.

| # | File | Qty | Infill | Walls | Supports | Orientation on the bed | Note |
|---|---|---|---|---|---|---|---|
| 01 | `dona_univ_robot_hand_2026-11-13_Sanjev_01_fittest_servoseat.stl` | 1 | 30 % | 3 | no | as exported (flat, open top up) | ~10 min. **Print first**, test one servo (guide step 2) |
| 02 | `dona_univ_robot_hand_2026-11-13_Sanjev_02_servoadapter_es08ma_ii_x5.stl` | 5 | 40 % | 4 | no | as exported (arrow face up) | One per finger servo |
| 03 | `dona_univ_robot_hand_2026-11-13_Sanjev_03_pulley_es08ma_ii_x5.stl` | 5 | 100 % | — | no | as exported (flat top on the bed, horn pocket up) | |
| 04 | `dona_univ_robot_hand_2026-11-13_Sanjev_04_wristlarge_official.stl` | 1 | 30 % | 2 mm | no | as exported | **You already printed this — reuse it.** |
| 05 | `dona_univ_robot_hand_2026-11-13_Sanjev_05_fingers_official_plate.stl` | 1 plate | 30 % | 2 mm | no | as exported | Finger segments |
| 06 | `dona_univ_robot_hand_2026-11-13_Sanjev_06_fingertips_official_plate.stl` | 1 plate | 30 % | 2 mm | **yes** | as exported | 5 tips |
| 07 | `dona_univ_robot_hand_2026-11-13_Sanjev_07_fingercover_official.stl` | 1 | 30 % | 2 mm | **yes** | as exported | |
| 08 | `dona_univ_robot_hand_2026-11-13_Sanjev_08_palmcover_official.stl` | 1 | 30 % | 2 mm | **yes** | as exported | Palm-side shell |
| 09 | `dona_univ_robot_hand_2026-11-13_Sanjev_09_handcover_jinielogo.stl` | 1 | 30 % | 2 mm | **yes** | as exported | Back-of-hand shell with the Jinie EduTech logo (replaces the official HandCover) |
| 10 | `dona_univ_robot_hand_2026-11-13_Sanjev_10_deskstand.stl` | 1 | 25 % | 3 | no | as exported (base on the bed) | Holds the hand upright for testing |

STEP files (`01`, `02`, `03`, `10`) are clean CAD solids for Fusion 360 / FreeCAD. The official parts (04–09) exist only as meshes, so STL only.
If official parts fit too tight, set slicer "horizontal expansion" to about −0.15 for 05–08.

Not needed for the prototype (kept in `../original/`): official `i2_PulleyX5V1` (wrong spline), `i2_FingersMoldX5V3` (no sensors),
`i2_WristGearV1` (needs the InMoov forearm), `i2_HandCoverV1` (replaced by 09), the PDI6225 covers and `i2_Adapter1109MG`.
