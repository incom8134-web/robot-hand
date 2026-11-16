# CAD — HAEBOT Hand

> **Superseded on 2026-11-16.** The finger servos moved to **5 x Feetech STS3215 (12 V) in the forearm**, one per finger. The palm-mounted EMAX ES08MA II arrangement that `prototype/` was built around is the earlier plan. The new forearm servo bed and the STS3215 pulleys **have not been designed yet** — see [`../electronics/version_2/dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md`](../electronics/version_2/dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md). Nothing here has been deleted; the files below are kept as they were.

Only two folders:

| Folder | What it is |
|---|---|
| [`prototype/`](prototype/) | **The earlier prototype with the EMAX ES08MA II servos we own (superseded 2026-11-16, kept for reference).** One flat folder, files numbered in print/assembly order (`01_…` to `10_…`), STL to print + STEP for our parts, [`dona_univ_robot_hand_2026-11-13_Sanjev_print_list.md`](prototype/dona_univ_robot_hand_2026-11-13_Sanjev_print_list.md), [`dona_univ_robot_hand_2026-11-14_Sanjev_assembly_guide.md`](prototype/dona_univ_robot_hand_2026-11-14_Sanjev_assembly_guide.md), images (`img_…`) and the one generator script (`dona_univ_robot_hand_2026-11-13_Sanjev_99_build_prototype.py` + `dona_univ_robot_hand_2026-11-13_Sanjev_99_parameters.yaml`). |
| [`original/`](original/) | The **unmodified** official InMoov Hand i2 files and the forearm servo bed, kept as downloaded (with checksums). The hand geometry still applies to the current design; the stock forearm bed does not fit the STS3215. Do not print from here for the ES08MA prototype. |

Old folders (`01_official_*`, `02_haebot_modified`, `03_one_finger_test`, `04_forearm_servo_bed`, `04_jinie_branding`, `src`, `renders`)
were removed on 2026-11-13 to stop the confusion. They are still in git history (last version: commit `4d52bfb`).
The Jinie logo source files moved to [`../docs/brand/`](../docs/brand/).
