# Prototype A (P1) — 5 x STS3215 in the palm, stock-size InMoov forearm, board + power in the base

**Status 2026-11-17:** full arm generated in CAD from the original InMoov files (hand scaled 1.28x for the servos; forearm = **stock InMoov width (1.0x)**, lengthened: elbow half x1.35, wrist half x1.10 (250 mm), so it keeps the InMoov cone and looks like the reference; the hand overhangs the wrist a little, as on the stock InMoov). **Not printed yet** — print `00` first.
Real CAD exports from the scripts below (not concept images). InMoov © Gaël Langevin, CC BY-NC 3.0, non-commercial.

## Folders
| Folder | What |
|---|---|
| `print/1_hand/` | hand parts to print (00–04) |
| `print/2_forearm/` | forearm parts to print (05–06) |
| `print/3_base/` | base parts to print (10–12) |
| `reference/` | servo, board and PSU envelopes for checking — **do not print** |
| `assembly/` | `asm_P1_full_arm.step` — the whole arm in one STEP for **Fusion 360 / SolidWorks** (view only) |
| `reports/` | check results (JSON) written by the scripts |
| `images/` | preview images written by the scripts |
| `scripts/` | the generators — the source of every file above |

3D parts have short names. Older documents, reports, images and scripts use `dona_univ_robot_hand_YYYY-MM-DD_Sanjev_A_<name>`; new files get short names (user 2026-11-17).

## Print list
| No. | File | Qty | From InMoov | What changed |
|---|---|---|---|---|
| 00 | `print/1_hand/00_fit_test_middle_slot.stl` | 1 | cut from 01 | **print first**: one servo slot, test with a real STS3215 |
| 01 | `print/1_hand/01_palm_frame.stl` | 1 | `i2_WristLargeV2` x1.28 | 5 STS3215 pockets in the 5 stock slots (45.4 x 24.8 + 0.3/side) |
| 02 | `print/1_hand/02_back_cover.stl` | 1 | `i2_HandPDI6225V2` x1.28 | **widened to the frame outline with a lip down to the frame** (hides servos, pulleys, frame sides; knuckles, thumb joint and wrist left open), ≥ 2.4 mm over every pulley; servo tops + pulleys carved inside; InMoov text filled; **Jinie EduTech logo** engraved 1 mm |
| 03 | `print/1_hand/03_palm_cover.stl` | 1 | `i2_PalmCoverV2` x1.28 | servo bottoms + plugs carved; **closed** (≥ 1.9 mm skin) with smooth local bulges up to 3 mm where the servos would break through |
| 04 | `print/1_hand/04_ring_pulley_x5.step/.stl` | **5** | new | clamps on the Feetech Ø20 disc horn (4 x M2), tendon groove Ø26 |
| 05a–d | `print/2_forearm/05a_forearm_robpart2.stl` … `05d_forearm_robpart5.stl` | 1 each | `robpart2V4`–`5V4` **1.0x wide; 05c/05d x1.35 long, 05a/05b x1.10 long** | only 4 x M3 radial holes for the wrist block. Exported standing (print orientation, z = 0) |
| 06 | `print/2_forearm/06_wrist_block.stl` | 1 | new | fixed wrist: plug in the forearm top + tongue for the hand prongs (M10 bolt), 3 cable slots |
| 10 | `print/3_base/10_base_pan.step/.stl` | 1 | new | SMPS (Mean Well LRS-350-12) along the back; **100 x 60 board front-left on 4 M3 standoffs**; mains corner front-right with **your inlet (makePCB P087: C14 + fuse + switch, screw mount 2 x M3) in the right side wall** — cutout 48.8 x 28.3, holes 40 mm apart are ESTIMATES, measure the part; USB mini-B front; vents; feet |
| 11 | `print/3_base/11_base_lid.step/.stl` | 1 | new | socket shaped to the real InMoov elbow end (+1 mm/side, 20 mm high), cable hole 40 x 20 (servo bus cable), vents, "230V" mark |
| 12 | `print/3_base/12_psu_strap_x2.step/.stl` | **2** | new | PSU hold-down straps (M3 heat-set) |
| — | stock InMoov at **128 %** | | `i2_FingersX5V2`, `i2_FingersTipX5V2`, `i2_CoverFingerV3` | knuckle pins Ø4.2. `reference/ref_fingers_placed.stl` = look-only placement for renders |

Sizes: palm frame 144 x 176 x 31 mm; hand with covers 144 x 180 x 65; forearm 250 long (stock width); base **238 x 217 x 66** (was 270 x 232 x 72).
Full arm ≈ 587 mm tall with fingers. Base layout (SMPS + board + mains zone): `images/..._img_13_base_layout.png`.

## Full assembly (STEP)
`assembly/asm_P1_full_arm.step` (≈ 127 MB, higher detail so the curved covers look right): hand + fingers, 5 x STS3215 (Feetech model), 5 pulleys, forearm, wrist block, board envelope (in the base),
base pan, lid, PSU straps + PSU envelope — all in their assembled positions, named and coloured like the reference (white hand, black palm side, silver arm, silver pan + white lid).
Base, pulleys, straps and servos are exact CAD solids. The InMoov-derived parts are **simplified faceted solids for viewing** —
print from the STLs in `print/`, not from this STEP. Units mm, Z up (base on the table).

## Checks (from `reports/`)
- All printable STLs are closed volumes.
- Servo vs hand parts 0.0 mm³ (all 5); thinnest wall between pockets 1.76 mm (index–middle).
- Hand vs wrist block 0.0, hand vs forearm 0.0, forearm vs base lid 0.0 mm³; wrist block vs forearm shells 0.0 mm³; board vs base 0.0 mm³.
- PSU and inlet vs base 0.0 mm³.

## Run (in `scripts/`, in this order)
`..._A_build_hand.py` → `..._A_build_forearm.py` → `..._A_build_base.py` → `build_fingers_ref.py` → `layout_base.py` → `..._A_render_hand.py` → `..._A_render_base.py` → `..._A_render_assembly.py` → `..._A_build_assembly_step.py`
Needs: numpy, scipy, trimesh, manifold3d, shapely, cadquery, matplotlib, fast-simplification, ezdxf. Folder layout is defined only in `..._A_paths.py`.
Inputs (read-only, SHA-256 checked): `cad/original/hand_i2/`, `cad/original/inmoov_forearm/`, `cad/original/sts3215/`, logo `docs/brand/..._jinie_icon_logo2d.dxf`.

## Not verified / open (next agent: start here)
1. **Print 00 with a real servo first**; adjust `CLR` in the hand script if too tight/loose.
2. Back cover 02: the stock InMoov cover already touches the frame by 9 mm³ at one screw boss (x 32, y 55) — check at assembly. The new cover edge is a 0.5 mm height-map: sand lightly.
3. Palm cover 03: the plug zone under each servo is an ESTIMATE (`PLUG_LEN` 8 mm); check with the real cables.
4. Tendon path pulleys → fingers not modelled; fingers at 128 % not tested.
5. Forearm assembly of the InMoov print files was fitted (seams ≤ 1.1 mm) — dry-fit the printed shells.
6. Board (in the base): mounting holes / connectors TBD until the real board exists. Forearm: width `FA_SCALE`, length `FA_LEN` in the forearm script.
7. Base: verify PSU terminal end + fan side, the bought inlet cutout (snap-in panel 1.6 mm), USB extension holes; PSU switch to 230 V; protective earth; mains wiring by a qualified person.
8. Stability: hand ≈ 0.75 kg at ≈ 0.5 m (estimate) — add weight in the base if it tips.
