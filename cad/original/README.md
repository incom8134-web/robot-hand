# Original InMoov files (unmodified)

Kept exactly as downloaded from inmoov.fr on 2026-11-11 — see `SHA256SUMS.txt` (run `sha256sum -c SHA256SUMS.txt` here).
These are for the **later build with big servos** (JX PDI-6225MG / MG996R class). For the ES08MA II prototype use `../prototype/`.

| Folder | Files |
|---|---|
| `hand_i2/` | All 13 Hand i2 files: `i2_WristLargeV2`, `i2_FingersX5V2`, `i2_FingersTipX5V2`, `i2_CoverFingerV3`, `i2_PalmCoverV2`, `i2_HandCoverV1`, `i2_WristGearV1`, `i2_PulleyX5V1` (JX spline), `i2_FingersMoldX5V3` (silicone tip mould), `i2_PalmPDI6225V3` + `i2_HandPDI6225V2` (covers for big servos in the palm), `i2_Adapter1109MG` (official small-servo adapter + pulley), `Calibrator` |
| `forearm_servo_bed/` | `RobServoBedV6` (right) and `LeftRobServoBedV6` — only needed if the finger servos go in the forearm |

How InMoov says the Hand i2 can be built (inmoov.fr/inmoov-hand): (1) JX PDI-6225MG-300 servos in the forearm servo bed,
(2) the same servos mounted directly in the palm (WristLarge slots, PDI6225 covers), (3) small JX-PDI1109MG / SG90-type
servos in an adapter in the palm, with elastic thread instead of springs. **The prototype uses option 3.**

**License:** InMoov © Gaël Langevin, CC BY-NC 3.0 — attribution required, non-commercial only. See `../../ATTRIBUTION.md`.
