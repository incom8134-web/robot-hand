# Original InMoov files (unmodified)

Kept exactly as downloaded from inmoov.fr on 2026-11-11 — see `dona_univ_robot_hand_2026-11-13_Sanjev_sha256sums.txt` (run `sha256sum -c dona_univ_robot_hand_2026-11-13_Sanjev_sha256sums.txt` here).
These are the reference geometry for every build. The current design (2026-11-16) puts **5 x Feetech STS3215 (12 V) in the forearm**, one per finger; the stock forearm bed here is sized for the JX PDI-6225MG / MG996R class and is too small for them, so a new bed is to be designed. For the earlier ES08MA II prototype use `../prototype/`.

| Folder | Files |
|---|---|
| `hand_i2/` | All 13 Hand i2 files: `i2_WristLargeV2`, `i2_FingersX5V2`, `i2_FingersTipX5V2`, `i2_CoverFingerV3`, `i2_PalmCoverV2`, `i2_HandCoverV1`, `i2_WristGearV1`, `i2_PulleyX5V1` (JX spline), `i2_FingersMoldX5V3` (silicone tip mould), `i2_PalmPDI6225V3` + `i2_HandPDI6225V2` (covers for big servos in the palm), `i2_Adapter1109MG` (official small-servo adapter + pulley), `Calibrator` |
| `forearm_servo_bed/` | `RobServoBedV6` (right) and `LeftRobServoBedV6` — the finger servos do now go in the forearm, but these stock beds are too small for the STS3215 (45.2 x 24.7 x 35 mm each). Kept as the reference the new bed is drawn against |

How InMoov says the Hand i2 can be built (inmoov.fr/inmoov-hand): (1) JX PDI-6225MG-300 servos in the forearm servo bed,
(2) the same servos mounted directly in the palm (WristLarge slots, PDI6225 covers), (3) small JX-PDI1109MG / SG90-type
servos in an adapter in the palm, with elastic thread instead of springs. The earlier ES08MA II prototype used **option 3**. The current design (2026-11-16) is closest to **option 1**, servos in the forearm, but with 5 x STS3215 on a new bed rather than the stock one.

**License:** InMoov © Gaël Langevin, CC BY-NC 3.0 — attribution required, non-commercial only. See `../../dona_univ_robot_hand_2026-11-13_Sanjev_attribution.md`.
