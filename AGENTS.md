# AGENTS.md — HAEBOT Hand (STS3215): how AI agents and people work together

Read this file first — it is the only hand-over file (the log is in section 9; `docs/agents/` was removed by the user). If this account runs out of credit, the next agent continues from here.
Last updated: 2026-11-26 KST (Grok Bot) — Prototype A review fixes. See section 9.

## 1. Project in one paragraph
HAEBOT Hand is an **educational 5-finger, tendon-driven robot hand** by Genie EduTech (Busan) for physical-AI / Python classes.
Mechanics come from the open-source **InMoov Hand i2** (Gaël Langevin, **CC BY-NC 3.0, non-commercial**; credits in
`dona_univ_robot_hand_2026-11-13_Sanjev_attribution.md`). A PC (Python + OpenCV + MediaPipe) sends finger values over USB to a custom
board that drives **5 x Feetech STS3215 12 V serial-bus servos** (ST-3215-C018).
Any 3D image that is not a CAD export is a conceptual image, not a real model — say so wherever one is used.

## 2. User rules (2026-11-17) — follow exactly
1. **Do not design from scratch. Only modify the original InMoov files** in `cad/original/` (read them, never edit them).
   Keep the InMoov look; if something does not fit, enlarge/modify the InMoov part, do not replace it with a new shape.
2. Two prototypes, worked on **separately**, in two folders:
   | Folder | Layout | Status |
   |---|---|---|
   | `cad/prototype/A_servos_in_palm/` (**P1**) | **all 5 STS3215 in the palm** (InMoov "servos in the palm" option; user photo) + **controller board 100 x 60 in the forearm** + **power base** | **full arm generated** (hand, logo, forearm + board tray, base); not printed |
   | `cad/prototype/B_servos_in_forearm/` | **all 5 STS3215 in the forearm**, stock-size InMoov hand (InMoov reference build, user photo). Backup in case A is too heavy | **not started** |
3. The user deleted everything else (old ES08MA prototype moved to `cad/_to_delete/` — the user deletes it).
4. Keep folders neat: no stray copies, no `__pycache__`, no test exports.
5. Save locally, the user reviews, the user says when to commit/push. Never push on your own.

## 3. Folder ownership
| Owner | May edit | Notes |
|---|---|---|
| Agent working on A | `cad/prototype/A_servos_in_palm/` | |
| Agent working on B | `cad/prototype/B_servos_in_forearm/` | may be the same agent, one folder at a time |
| User (human) | `electronics/` | agents do **not** redesign electronics; they reserve space and cable paths and ask |
| Shared (edit with a log entry in section 9) | `AGENTS.md`, `cad/README.md`, root `README.md` | |
| Read-only | `cad/original/` (InMoov hand i2, `inmoov_forearm/` robpart2-5V4, forearm servo bed, `sts3215/` Feetech STEP; SHA-256 in the sums file / folder READMEs) | scripts must check the hashes |

## 4. STS3215 (ST-3215-C018) — numbers for CAD
Source: Feetech STEP `cad/original/reference/servo-motor_sts3215-v10.step` (moved 2026-11-22, same SHA-256) (measured) + box label (A 45.22 / B 24.7 / C 35 mm).
| Item | Value (STEP frame: x long side, horn end +x, shaft +z, origin = case centre) |
|---|---|
| Case | x −22.7…22.7, y −12.4…12.4, z −18.3…17.0 → **45.4 x 24.8 x 35.3 mm** |
| Shaft | x = +12.5 (10.2 mm from the horn end), y = 0 |
| Disc horn | Ø20, z 14.7…18.7 (hub Ø9 14.7…16.2, disc 16.2…18.7); horn screw top z 21.07; 4 holes at (±5, ±5) from the shaft (verify on the real horn) |
| Connectors | 2 x 5264-3P on the bottom face, x −6…3, z down to −21.1 (2.8 mm out of the case); add ≈ 8 mm for the plug + bend (estimate) |
| Mounting | **no ears** → hold by pockets + clamps/covers |
| Mass / electrical | 55 g; 12 V: stall 2.7 A @ 30 kg·cm, rated 0.9 A. Electronics = user |

## 5. Prototype A interface summary (see its README for everything)
- Parts = InMoov `i2_WristLargeV2`, `i2_HandPDI6225V2`, `i2_PalmCoverV2` scaled **1.28x** + STS3215 pockets; new ring pulley x5.
- Fingers, fingertips, finger covers (and `i2_WristGearV1` if used) are printed **stock files at 128 %**; knuckle pins Ø4.2, wrist pin Ø10.6.
- Wrist side is the scaled InMoov wrist (no interface to prototype B; B uses the stock-size hand).

## 6. CAD conventions
- Units mm, Z-up. Prototype frames = InMoov i2 WristLargeV2 frame (x across the hand, +x thumb side, −y fingers, +y wrist).
- Source of truth = Python generators in `<prototype>/scripts/`; parameters in CAPS at the top with *measured / datasheet / estimate / TBD*.
- No STL/STEP without the script that makes it. Mesh-derived InMoov parts are exported as STL (a faceted STEP would be huge); new parametric parts as STEP + STL.
- Preview PNGs from a render script; servo = the Feetech STEP model.
- **Prototype folder layout (user decision 2026-11-17):**
  ```
  <prototype>/README.md
  <prototype>/print/1_hand/ , print/2_forearm/ , print/3_base/   parts to print
  <prototype>/reference/        ref_* envelopes - do not print
  <prototype>/assembly/         asm_* STEP assembly for Fusion 360 / SolidWorks (view only)
  <prototype>/reports/          JSON check results
  <prototype>/images/           preview PNGs
  <prototype>/scripts/          generators + <prefix>paths.py (the only place the layout is defined)
  ```
- **File naming (user decision 2026-11-17):** 3D parts (STL/STEP) get **short names** `<nn>_<part>.<ext>` (e.g. `01_palm_frame.stl`, `ref_board_100x60.stl`).
  Documents, reports, images and scripts follow the repo convention `dona_univ_robot_hand_YYYY-MM-DD_Sanjev_<A|B>_<name>.<ext>`. `README.md` / `AGENTS.md` stay plain.
- **Wiggle room is mandatory (user rule 2026-11-17):** every printed part that fits onto/into something gets clearance — never model a fit at 0.
  | Fit | Clearance (per side unless noted) |
  |---|---|
  | servo / board / PSU pocket | 0.3 |
  | part sliding into another printed part (tongue in prongs, plug in a shell, hook in a slot) | 0.4–0.5 |
  | printed part over a bought part (pulley over the servo horn) | 0.2 (snug) |
  | big printed parts nesting (forearm in the base socket) | 1.0 (+ tape/TPU shim) |
  | holes: M3 clearance Ø3.4, M3 heat-set Ø4.0, M2 clearance Ø2.2, M10 Ø10.5 | — |
  Put the clearance in a named parameter, report it, and make a small fit-test print for every new critical fit.

## 7. Protocol
1. Before work: read section 9 (newest entry first). 2. Work only in your folder. 3. After work: add an entry to section 9:
what changed, files, verified / not verified, open questions. Unknowns are **TBD**, never guessed silently. 4. The user decides open questions.

## 8. Git
Branch `servo-24x12`. Never commit/push to `main` or rewrite history without the user's approval. One logical change per commit
(`protoA: ...`, `protoB: ...`). Do not commit slicer output (`*.gcode`, `*.3mf`), caches, `Claude outputs/`, or `cad/_to_delete/`.

## 9. Log (newest first) — hand-over between agents

### 2026-11-26 KST — Grok Bot (project manager) — P1 review fixes (user approved commit + merge)
- **User decisions:** go with Prototype A; office printers Bambu Lab P1S + Two Trees Sapphire Plus (Kossel = home only) → **no part splitting**; keep the **chained 12 V servo power** and the **LRS-350-12 inside the base** with a PC-style IEC cable (do not change the circuit).
- **Hand script:** servo STEP path → `cad/original/reference/`; ring pulley 04 redesigned (was colliding with the servo case 63–123 mm³): cap on the horn + 1.2 mm skirt, M2 counterbores, tie hole; 5 x M3 heat-set pockets Ø4.0 x 6 in the frame; palm cover 8 x 5.5 mm cable channel from all plug pockets to the wrist; back cover 8 vent slots over the motor ends.
- **Forearm script:** wrist tongue end square, `TONGUE_END_GAP` 0.5 mm to the palm root (`TONGUE_FLAT_END`); shells 05a–d byte-identical.
- **Verified (box):** all print STLs watertight; servo vs parts 0.0 mm³; pulley vs case/horn/screw 0.0; back-cover skin ≥ 2.4; palm skin ≥ 1.94, under channel ≥ 1.92; voxel test: every plug pocket reaches the wrist exit (≥ 3 mm passage); hand vs block / forearm / lid 0.0 at 0°; wrist free rotation ≈ −3…+2.5° (was ±3–5°).
- **Docs:** README banner/architecture → Prototype A + user's power; Prototype A README: print settings, fasteners, electrical safety notes (12 V fuse ≈ 7.5 A, firmware torque limits, inlet T4A, earth to PSU FG, terminal cover).
- **Not done / open:** tendon path pulleys → fingers (needs real finger holes / PTFE guides at assembly); `assembly/asm_P1_full_arm.step` not regenerated (old pulley; > 100 MB); tipping only documented (feet / clamp / ballast); nothing printed or tested.

### 2026-11-17 18:00 KST — Claude — P1: render + STEP colours, USB close-up
- Renders: brighter shading + light grey background so white parts read; hand renders (img_01-04) now white frame/back cover + black palm cover. STEP colours: white hand, black palm cover, silver (0.56) arm + wrist block + base pan, white lid.
- USB mini-B hole was already in the pan front wall (14 x 9 + 2 x M3 at 28 mm, x = USB_X, z = 28); new `img_14_base_usb_closeup.png` shows it.

### 2026-11-17 17:50 KST — Claude — P1: colours, longer elbow half, smaller base with the user's inlet
- Colours (user): palm side (03) black, other hand parts white, forearm + wrist block silver, base pan silver + lid white (renders + STEP).
- Forearm: elbow half (05c/05d) x1.35 long, wrist half (05a/05b) x1.10, width stock 1.0x → 250 mm. Lid collar 28 → 20 mm so more arm shows.
- Base v2 238 x 217 x 66 (was 270 x 232 x 72): SMPS along the back, board front-left, mains corner front-right with the user's inlet
  (makePCB P087, C14 + fuse + lit rocker, SCREW mount) in the RIGHT side wall; partition at x = PART_X; AC wires to the SMPS terminal end
  through the channel beside it. Inlet sizes are ESTIMATES (cutout 48 x 27.5 + 0.4/side, 2 x M3 at 40 mm) — measure the real part.
  USB moved to the front between board and mains corner. `layout_base.py` → `img_13_base_layout.png`.
- Fixed: render/STEP placed the arm at the old 72 mm base height; now read from the base report.
- Checks: hand / wrist block / forearm / lid / board / SMPS / inlet overlaps 0.0 mm³; all print STLs watertight.

### 2026-11-17 17:30 KST — Claude — P1: longer arm, full back cover, base layout
- **User:** liked the look; arm a little longer; cover the rest of the hand; explain how the SMPS + board fit in the base; asked why the palm cover looked odd in the STEP.
- **Done:** forearm length x1.15 (`FA_LEN`, width stays stock 1.0x) → 234 mm. Back cover 02 widened to the frame outline (height-map extension of the stock dome + 2.4 mm lip down to the frame, 0.4 mm clearance; knuckles, thumb joint, wrist open) — pinky pulley skin now 2.4 mm (was 0.7).
- Palm cover in the STEP looked faceted because it was decimated to 1500 faces; STEP detail raised (covers 8-9k faces, forearm 3k) → 126 MB. The print STLs were always full detail (`img_23` compares them).
- New `scripts/layout_base.py` → `img_13_base_layout.png` (top view: SMPS back, board front-left, mains zone, inlet, USB, socket, wiring).
- Checks: all part overlaps 0.0 mm³ except the stock InMoov back-cover boss vs frame 9 mm³ (unchanged from stock); all print STLs watertight.

### 2026-11-17 17:05 KST — Claude — P1: reference look (stock forearm, board in base, closed palm, fingers, colours)
- **User:** the tapered arm still looked thick vs the hand; "make it smaller", board may move to the base; no long file names for new files.
- **Done:** forearm = stock InMoov 1.0x evenly scaled (`FA_SCALE` in build_forearm; 0.9 / 1.1 also build) — the InMoov cone is back, length 203 mm. Board tray (07) removed; the 100 x 60 board now sits in the base on 4 M3 standoffs (front-left, x 15..115, y 24..84); lid cable hole 40 x 20 (STS3215 = serial bus, one 3-wire cable up the arm). Wrist block cable slots adapt to the slimmer arm (3).
- Palm cover 03 is now **closed** (≥ 1.9 mm skin over the servo bottoms/plugs) with smooth local bulges up to 3 mm.
- New `scripts/build_fingers_ref.py` → `reference/ref_fingers_placed.stl` (stock i2 fingers x1.28 on the measured knuckle holes; thumb approximate, look only).
- Renders + STEP use the reference colours (white, blue covers / elbow half / lid, red wrist).
- Checks: hand / wrist block / forearm / lid 0.0 mm³; board vs base 0.0; all print STLs watertight. STEP ≈ 67 MB.
- **Device cleanup:** `print/2_forearm/07_board_tray.stl` moved to `cad/_to_delete/`.
- **Open (user):** shorten the existing long file names too?

### 2026-11-17 16:45 KST — Claude — P1: slim tapered forearm
- **User request:** forearm looked fat vs the stock InMoov photo. Keep the palm (1.28x for STS3215), make the arm slim and tapered to match the hand; board low if it doesn't fit high.
- **Done:** `..._A_build_forearm.py` now warps the InMoov shells instead of scaling them: cross-section 1.0x at the elbow → 1.28x at the wrist (linear), length x1.28 (260 mm). Shells are subdivided to 6 mm edges before the warp. Elbow end = stock size (≈ 87 x 79); wrist end = hand size, no step.
- **Board stays HIGH** (tray z 140–246, just below the wrist): only 0.46 cm³ of inner rib is cut (limit 2 cm³, asserted in the script).
- Forearm STLs are now exported standing (z = 0); the print→assembly 4x4 per part is in `reports/..._A_report_forearm.json` (`print_to_assembly`), used by the render + STEP scripts. Base lid socket rebuilt from the new elbow outline.
- Checks: hand / wrist block / forearm / base lid overlaps 0.0 mm³; all print STLs watertight. Images 20–22 and `assembly/asm_P1_full_arm.step` (≈ 56 MB) regenerated.
- **Open (user):** keep the box base or make a round base (≈ Ø250–260)?

### 2026-11-17 17:10 KST — Claude — P1 STEP assembly
- New `scripts/..._A_build_assembly_step.py` → `assembly/asm_P1_full_arm.step` (≈ 53 MB, 64 solids, named + coloured, assembled positions). Exact solids: base, lid, straps, pulleys, Feetech servo STEP; InMoov-derived parts as simplified faceted solids (view only, print from STLs).
- Back cover logo fill now on a 1.0 mm grid (was 0.5) and the servo pockets are carved AFTER the logo (the fill had closed 0.3 mm³ of the ring pulley pocket). All checks back to 0.0 mm³.

### 2026-11-17 16:50 KST — Claude — P1 folder reorganised
- `cad/prototype/A_servos_in_palm/` now has `print/1_hand`, `print/2_forearm`, `print/3_base`, `reference/`, `reports/`, `images/`, `scripts/` + README (print list per folder). 3D parts renamed to short names; docs/reports/images/scripts keep the convention. Scripts renamed: `..._A_build_hand.py`, `_build_forearm.py`, `_build_base.py`, `_render_hand.py`, `_render_base.py`, `_render_assembly.py`; new `..._A_paths.py` holds the layout.
- All six scripts re-run in the new layout: same results (all printable STLs closed volumes; every fit check 0.0 mm³). Added `00_fit_test_middle_slot.stl` (one slot cut from the palm frame) — print it first with a real servo.
- Old flat files were moved to `cad/_to_delete/A_old_flat/` (user deletes).

### 2026-11-17 16:30 KST — Claude — P1 forearm + full arm done
- Official InMoov forearm `robpart2V4`–`5V4` copied (user granted access) to `cad/original/inmoov_forearm/` (hashes in its README). The files are in print orientation; assembly was **fitted**: robpart3 tilt 1.0° about x, y −40.47, z +1.0 (seam gaps ≤ 1.1 mm); robpart4 y −42.5; wrist half on the elbow half at z +105.6. (Codex's earlier "96.66 x 49.18" lower-forearm size came from the un-assembled files — wrong; do not reuse.)
- New in `cad/prototype/A_servos_in_palm/`: `..._A_forearm_build.py` → parts 05a–d (InMoov shells x1.28, 4 x M3 radial holes, 0.6 cm³ rib trimmed in robpart2; exported in InMoov print orientation), 06 wrist block (**fixed wrist**: plug + tongue for the hand prongs, M10 bolt, 2 cable slots), 07 board tray (100 x 60 board standing along the arm just below the wrist). Base socket now follows the real elbow-end outline (+1 mm/side), 28 mm deep. `..._A_assembly_render.py` = full arm + fit check.
- Hand wrist prongs were **measured on the scaled frame** (gap 41.84 at x −17.41, height 0…25.27, pin y 106.12 z 13.96, hole ≈ 10.2–11.5) — earlier rounded numbers were off by ~1 mm.
- Verified: all printable STLs are closed volumes (safe_export re-merges with manifold3d); hand vs wrist block / forearm, forearm vs base lid, board / tray / block vs shells = 0.0 mm³ (block vs tray 0.8 mm³ at the hook — negligible). Full arm 519 mm tall without fingers (+≈ 125 mm fingers).
- Not verified: no print; forearm seam fit of the printed shells; board holes/connectors (TBD); tendon path pulleys → fingers; arm stability on the base (hand ≈ 0.75 kg at ~0.55 m — estimate; add weight to the base if it tips).
- Open (user): wrist rotation later (InMoov `i2_WristGearV1` + 6th servo)? upper arm? prototype B next?

### 2026-11-17 15:30 KST — Claude — P1: company logo on the hand, power base; forearm blocked
- **User decisions:** P1 = prototype A (5 servos in the palm). The controller board (100 x 60) goes **in the forearm**. Full arm + base. Mains via **PC power cable** (IEC C14 fused + switched inlet). Company logo on the hand instead of the InMoov logo.
- **Done (cad/prototype/A_servos_in_palm/):**
  - `02_back_cover`: the engraved "InMoov" text is filled to the cover's own dome; the Jinie icon (from `docs/brand/..._jinie_icon_logo2d.dxf`) + "JINIE EDUTECH" engraved 1.0 mm, following the dome.
  - Base `10_base_pan`, `11_base_lid`, `12_psu_strap_x2` (CadQuery, STEP + STL): 270 x 232 x 72 mm (+4 lid, +40 socket). Mean Well LRS-350-12 at the back on 5 mm rails, held by 2 straps; L-partition walls off the mains corner; IEC C14 inlet vertical in the back wall (panel thinned to 1.6 mm for snap-in; cutout 28 x 47.5 — set to the bought part); USB mini-B on the front; vents; zip-tie strain relief; 6 x M3 heat-set lid screws; rubber feet. Lid: forearm socket inner 127.7 x 67 x 40 (4 x M4 radial), cable hole 60 x 28 for 12 V + USB, "230V" mark. Checks: PSU + inlet envelopes vs base 0.0 mm³.
- **Blocked — next agent start here:** the P1 forearm (part 05) needs the official InMoov right-forearm STLs `robpart2V4.stl`–`robpart5V4.stl`. They are NOT in `cad/original/`; inmoov.fr and GitHub mirrors are blocked from the Claude workspace. The user (or an agent running on the PC) must copy them into `cad/original/inmoov_forearm/` and add SHA-256 lines to `cad/original/..._sha256sums.txt`. Then: scale 1.28x (matches the hand), keep the InMoov exterior, add a removable 100 x 60 PCB tray just below the wrist (board needs ≈ 62 mm inside width + 20–25 mm height — stock forearm inside is ≈ 83 x 63 at 42 mm below the wrist, x1.28 ≈ 106 x 81), cable channel to the base, and re-check the base socket against the real lower forearm.
- **Verify before printing the base:** LRS-350-12 terminal-block end + fan side; bought inlet cutout; USB extension holes; set the PSU input switch to 230 V; protective earth inlet → PSU FG; mains wiring by a qualified person. Base needs a ≥ 270 mm bed (or split the pan).
- **Open questions (user):** wrist fixed or rotating? Upper arm wanted, or forearm on the base only (current)?

### 2026-11-17 15:00 KST — Claude — fresh start, prototype A V1
- Two prototypes from the InMoov originals only. A (5 servos in the palm) V1: InMoov `i2_WristLargeV2`, `i2_HandPDI6225V2`, `i2_PalmCoverV2` scaled 1.28x with 5 STS3215 pockets in the stock slots, covers carved to sandwich the servos, ring pulley for the Feetech disc horn. Servo vs parts overlap 0.0 mm³, min wall 1.76 mm. Feetech STEP stored in `cad/original/sts3215/`. B (servos in the forearm) not started (same forearm files needed).
- Open in A: tendon path pulley → fingers not modelled; pinky back-cover skin 0.7 mm; servo bottoms show through the palm cover; horn hole pattern to confirm on a real horn.

## Palm (owner: Grok Bot) - updated 2026-11-22 KST — SUPERSEDED 2026-11-26: the user chose Prototype A (all 5 servos in the palm); this 3+2 plan is history only
- Palm V0 (from-scratch palm) is DROPPED. Do not use it.
- Current palm = original InMoov i2 parts, minimally modified for 3x STS3215 (THUMB, MIDDLE, RING):
  `cad/current_palm/i2_wristlargev2_STS3215.stl`, `i2_handpdi6225v2_STS3215.stl`, `i2_palmpdi6225v3_STS3215.stl` + README.md + previews.
- Forearm (owner: Codex) must hold the other 2 STS3215: INDEX and PINKY.
- Interface unchanged from i2: wrist prongs (34 mm gap, 8 mm pin), tendon guides at the wrist.
- Hand is +5.6 mm thicker on the back cover and +1.1 mm on the palm face, only at the 3 servo spots.
