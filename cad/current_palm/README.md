# cad/current_palm — InMoov i2 palm, minimally modified for 3x Feetech STS3215

Owner: Grok Bot (palm only). Arm + base: Codex (`cad/current/`). Date: 2026-11-20 (KST).
**Palm V0 (the from-scratch CadQuery palm) was DROPPED** — user wants the proven i2 design, only modified.

Status: CAD concept. **Not printed, not fit-tested.** All 3 STLs are watertight, 1 body each.

## Which servos
| Palm (3 x STS3215) | Forearm (Codex) |
|---|---|
| THUMB, MIDDLE, RING (each sits in its own stock i2 servo slot, enlarged) | INDEX, PINKY |

Why ring and not index: the index slot was tested too. To fit a 24.73 mm STS3215 there, the pocket
comes within 0.8 mm of the outer wall, the middle servo must move 7 mm, and the palm cover breaks
into 3 loose pieces. The ring slot keeps the outer shape intact. Switch only if you accept those changes.

## Files
| File | From original (cad/original/hand_i2/) | What changed |
|---|---|---|
| `i2_wristlargev2_STS3215.stl` | `..._i2_wristlargev2.stl` | 3 servo pockets cut through (z −1..26): 25.33 x 45.83 mm (= STS3215 24.73 x 45.23 **+0.3 mm clearance per side**). Outer size unchanged 112.57 x 137.65 x 24.53. One 202 mm³ sliver (x 34–47, y 34–38) that the thumb pocket cut loose was removed. Volume 84590 → 69293 mm³. |
| `i2_handpdi6225v2_STS3215.stl` (back cover) | `..._i2_handpdi6225v2.stl` | Servo pockets to 11.8 mm below the WristLarge back face, plus an 8 mm plug/cable well under the 2x 5264 connectors. Local **bumps 1.2 mm skin** around each pocket. **Back-cover thickness grows 15.56 → 21.16 mm (+5.6 mm), only at the 3 servo bumps**; rest unchanged. |
| `i2_palmpdi6225v3_STS3215.stl` (palm cover) | `..._i2_palmpdi6225v3.stl` | Clamp bars (8 mm wide, 14–22 mm from shaft toward wrist, 8 mm overhang each side) press the servo case top at z 23.2 → servo is clamped between back cover floor and these bars (STS3215 has no ears). Shaft holes Ø21.95, 4 mm tendon slots from each shaft to its original i2 tendon guide. **Pulley domes**: Ø25.15 ring, 1.6 mm wall, 1.2 mm roof, top at 35.7 mm → **palm face grows +1.1 mm over i2's max (34.58 → 35.7), locally at 3 domes**; cover length 118.38 → 122.46 mm (+4.1 mm) because the thumb dome sticks past the cover outline. |

Shaft moves vs original i2 servo axis (along / sideways / rotation): thumb 2.5 / 1.0 mm / 0°, middle 1.0 / 0 mm / 0°, ring 3.0 / 5.5 mm / 1°.
**Total hand thickness: about +6.7 mm at the servo spots (5.6 back + 1.1 palm).**
Unchanged: finger knuckle mounts, thumb joint, wrist prongs, outer outline of WristLarge, all other i2 parts.

Previews: `preview_top_before_after.png` (WristLarge before/after with green STS3215 ghosts), `preview_sections_before_after.png` (cut along each servo, ghost + pulley + plug zone).
Box copy + build scripts: `/workspace/palm_i2_mod/` (finalize.py, check.json); base build in `/workspace/sts3215_study/work/build2.py`.

## Not verified (must test with real parts)
1. Real STS3215 shaft offset (used 10.2 mm from case end; drawing does not dimension it).
2. Pulley: i2 pulley is Ø17 x 10 mm with a bore for the old servo — **needs a new 25T spline bore** (not made yet). Dome assumes pulley sits 0.5 mm above case top.
3. 5264 plug + cable bend depth (8 mm is an estimate) and cable exit to the wrist.
4. Servo footprint pokes past the back-cover outline: thumb 24 mm², middle 60 mm², ring 141 mm² (seen as small side openings) — check by eye after print.
5. Clamp force of the bars (no screws into the case yet; 4x PA3.0 holes on the servo bottom could be used later).
6. Tendon travel/angle change from the moved shafts; heat in a closed palm (70 °C cut-off).
7. Print orientation/supports for the new domes and bars.
