# CAD — HAEBOT Hand i2 V1

All dimensions in mm. Every number is tagged in [`parameters.yaml`](parameters.yaml):
`[SRC]` measured from the official STL · `[DS]` seller nominal · `[EST]` estimate · `[TBM]` to be measured.

> **Status: GENERATED — nothing here has been printed or fit-tested yet.**
> ES08MA II geometry comes from seller-nominal / estimated dimensions.
> **Print the fit coupon first**, measure your real servo, update `parameters.yaml`, rebuild.

## Folder map

```
cad/
├── parameters.yaml                  ← single source of truth (edit measured: values here)
├── 01_official_inmoov_i2/           ← UNMODIFIED InMoov Hand i2 files (CC BY-NC 3.0, Gaël Langevin)
├── 01_official_inmoov_forearm/      ← UNMODIFIED InMoov forearm servo bed (RobServoBedV6, CC BY-NC 3.0)
│   ├── print/                       ← print these as-is
│   ├── do_not_print/                ← not used in V1
│   └── SHA256SUMS.txt               ← checksums of the files as downloaded 2026-11-11
├── 02_haebot_modified/              ← OUR parts (step/ + stl/)
├── 03_one_finger_test/              ← one-finger test rig (step/ + stl/)
├── 04_forearm_servo_bed/            ← ES08MA II adapter plate for the official servo bed (step/ + stl/)
├── renders/
└── src/build_parts.py               ← CadQuery generator for all our parts
```

## Where the finger servos go

In the official design the 5 finger servos sit in the **forearm**, on the InMoov
**Simple Servo Bed** (inside `Robpart5`, with `RobCableFront` / `RobCableBack`).
The finger lines run from the hand to the servos through PTFE tubes
(thumb 335, index/middle/ring 300, pinky 360 mm) `[SRC: inmoov.fr/hand-i2]`.

### ES08MA II in the official servo bed → `HB_F01` adapter plate (×5)

The official `RobServoBedV6` is printed **unmodified**. Each of its 5 seats (3 front, 2 rear) gets one
`HB_F01_ServoBedAdapter_ES08MA-II` plate, screwed into the **original 4 holes** of that seat.

| | Original seat (measured from RobServoBedV6.stl) | ES08MA II | Difference |
|---|---|---|---|
| Body length (gap between rails) | 41.6 | 23.0 `[DS]` | −18.6 |
| Body width (floor opening) | 20.1 | 11.5 `[DS]` | −8.6 |
| Tab-hole pitch along servo | 49.8 (2 holes per tab, 9.5 apart) | ~27.5 `[EST]`, 1 hole per tab | −22.3 |
| Servo bottom → under tabs | 26.0 (floor 3.5 → rail top 29.5) | ~15.5 `[EST]` | −10.5 |
| Torque | ~10–13 kg·cm class | 1.6–2.0 kg·cm `[DS]` | ~6× weaker |

How the adapter works:
- 4.0 mm plate sits on the rail tops; open U-slots line up with the 4 original Ø3.07 holes (original screws).
- ES08MA II drops through the plate, tabs rest on top, 2 × M2 self-tap screws.
- **Shaft position = original servo shaft position** (10.15 mm from the seat centre, `[EST]` standard-servo offset).
- **Shaft height = original** (16.5 mm above the rail top `[EST]`), so pulleys, PTFE tubes, RobCableFront/Back,
  wrist and hand are unchanged. The original 3.4 mm lower rear-right seat is kept as designed.
- Plate is symmetric: the engraved **arrow points to the shaft end**. Turn it 180° to put the shaft at the other end —
  point it the same way your original servos' shafts face (toward the PTFE tube holes).
- Same plate fits the left-arm bed (`LeftRobServoBedV6` is a mirror image).

Digital check (`renders/HB_F01_ServoBed_assembly_check.png`): 5 plates + 5 servo models in the real bed, both
orientations, right and left bed → **0.00 mm³ interference**, all 20 original holes clear. Not yet printed.

![Servo bed assembly](renders/HB_F01_ServoBed_assembly_check.png)

## Print list

Official print settings `[SRC: inmoov.fr/hand-i2]`: 0.25 mm layer max, 30 % infill, 2 mm walls.
If official parts don't fit, InMoov suggests slicer horizontal expansion ≈ −0.15 as a starting point.

### Step 0 — tolerance check (print first)

| # | File | Qty | Supports | Purpose |
|---|---|---|---|---|
| 0a | `01_official_inmoov_i2/print/Calibrator.stl` | 1 | no | Official InMoov printer fit check |
| 0b | `02_haebot_modified/stl/HB_P00_FitCoupon_ES08MA-II.stl` | 1 | no | Drop your ES08MA II in → T-01 |

### Step 1 — one-finger test (before printing the whole hand)

| # | File | Qty | Supports | Notes |
|---|---|---|---|---|
| T01 | `03_one_finger_test/stl/HB_T01_OneFingerRig_Base.stl` | 1 | yes (pin bosses) | Clevis, PTFE/tendon guide tower, ES08MA II seat |
| T02 | `03_one_finger_test/stl/HB_T02_OneFingerRig_Washer.stl` | 2 | no | Spacers on the hinge pin either side of the knuckle |
| P03 | `02_haebot_modified/stl/HB_P03_Pulley_ES08MA-II.stl` | 1 | no | Keys onto the stock single-arm horn |
| — | one finger from `i2_FingersX5V2` + its tip from `i2_FingersTipX5V2` | 1 set | per official | Index finger recommended |

Hardware: 1 × ES08MA II, M3 × 25–30 screw or Ø3 mm rod as hinge pin, 2 × M2 self-tap screws (servo tabs),
0.8 mm braided line, PTFE 1.5/2.5 mm tube, elastic cord or 4.8 × 44.5 mm extension spring.

![One-finger rig](renders/HB_T01_OneFingerRig_check.png)

### Step 2 — hand (official parts, unmodified)

| # | File | Qty | Supports | Notes |
|---|---|---|---|---|
| O1 | `01_official_inmoov_i2/print/i2_FingersX5V2.stl` | 1 plate | no | 5 proximal + 4 middle segments |
| O2 | `01_official_inmoov_i2/print/i2_FingersTipX5V2.stl` | 1 plate | yes | Rigid printed fingertips |
| O3 | `01_official_inmoov_i2/print/i2_CoverFingerV3.stl` | 1 | yes | |
| O4 | `01_official_inmoov_i2/print/i2_PalmCoverV2.stl` | 1 | yes | Palm shell (official BOM part) |
| O5 | `01_official_inmoov_i2/print/i2_HandCoverV1.stl` | 1 | yes | Back-of-hand shell (official BOM part) |
| O6 | `01_official_inmoov_i2/print/i2_WristLargeV2.stl` | 1 | no | Wrist piece, bolts to RotaWrist3 |
| O7 | `01_official_inmoov_i2/print/i2_WristGearV1.stl` | 1 plate | no | Wrist rotation gear |
| P03 | `02_haebot_modified/stl/HB_P03_Pulley_ES08MA-II.stl` | 5 | no | On the ES08MA II servos, replaces i2_PulleyX5V1 |

### Step 3 — forearm servo bed

| # | File | Qty | Supports | Notes |
|---|---|---|---|---|
| B1 | `01_official_inmoov_forearm/print/RobServoBedV6.stl` | 1 | per official | Unmodified (right arm) |
| F01 | `04_forearm_servo_bed/stl/HB_F01_ServoBedAdapter_ES08MA-II.stl` | 5 | no (print flat) | One per seat, arrow → shaft end |

Other forearm parts (RobCableFront/Back, forearm shell, rotating wrist) are official and unmodified — not in this repo yet.
`01_official_inmoov_forearm/do_not_print/LeftRobServoBedV6.stl` is the left-arm version.

### Do NOT print (kept for reference only)

| File | Why |
|---|---|
| `i2_PulleyX5V1.stl` | Bore fits the JX-6225MG spline, not the ES08MA II → use **HB_P03** |
| `i2_FingersMoldX5V3.stl` | Mould for silicone tips with Hall-sensor magnets — V1 has no sensors |
| `i2_PalmPDI6225V3.stl`, `i2_HandPDI6225V2.stl` | Alternate palm/back variant, not on the official Hand i2 BOM |
| `i2_Adapter1109MG.stl` | Adapter for a different servo (1109MG) |

Reference-only CAD (never print): `HB_ES08MA-II_reference_dummy` (servo model for assemblies),
`HB_ES08MA-II_pocket_cutter` (negative used to cut an ES08MA II seat — reuse it in your own CAD).


## Branding — Hand Cover logo

`JE_HandCoverV1_JinieLogo` is the official Hand Cover with the engraved "InMoov" filled flush
and the Jinie EduTech icon + wordmark engraved in the same strip. See [`04_jinie_branding/README.md`](04_jinie_branding/README.md).

![Hand cover logo](04_jinie_branding/renders/closeup_before_after_icon_text.png)

## File formats

| Format | Status |
|---|---|
| **STL** | All parts |
| **STEP (B-rep)** | All our parts — clean solids generated by CadQuery |
| **Fusion 360 `.f3d`** | **Not included.** Only Fusion 360 can create one: Fusion 360 → *Upload* a `.step` → *Save* |
| **Editable parametric source** | `src/build_parts.py` + `parameters.yaml` |

## Rebuild after measuring your servo

```bash
pip install cadquery pyyaml
# edit cad/parameters.yaml -> fill measured: values (calipers)
python cad/src/build_parts.py
```

### Caliper checklist (`[TBM]` / `[EST]` → measured)

| Servo (ES08MA II) | Stock single-arm horn |
|---|---|
| body length / width / case height | arm length (shaft centre → tip) |
| tab span, tab thickness | hub diameter + height |
| case bottom → underside of tabs | arm width at hub and at tip |
| tab hole pitch + diameter | arm thickness |
| shaft centre → nearest body end | horn screw diameter |
| shaft height above case, spline Ø | |

## Open risks

- Shaft offset (10.15) and shaft height (16.5) of the original servos are `[EST]` standard-servo values.
  If your original pulley line-up differs, change `inmoov_forearm_servo_bed.std_*` and rebuild.

- ES08MA II torque (1.6–2.0 kg·cm `[DS]`) is far below the servos the InMoov forearm bed was designed for
  (MG946R / HK15298 class), and the line runs through 300–360 mm of PTFE tube (friction).
  Full finger flexion is **not verified** — the one-finger rig exists to test this first.
