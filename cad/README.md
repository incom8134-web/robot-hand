# CAD — HAEBOT Hand

Only two folders:

| Folder | What it is |
|---|---|
| [`prototype/`](prototype/) | **Everything for the prototype with the EMAX ES08MA II servos we own.** One flat folder, files numbered in print/assembly order (`01_…` to `10_…`), STL to print + STEP for our parts, [`PRINT_LIST.md`](prototype/PRINT_LIST.md), [`ASSEMBLY_GUIDE.md`](prototype/ASSEMBLY_GUIDE.md), images (`img_…`) and the one generator script (`99_build_prototype.py` + `99_parameters.yaml`). |
| [`original/`](original/) | The **unmodified** official InMoov Hand i2 files and the forearm servo bed, kept as downloaded (with checksums) for the later build with big servos. Do not print from here for the prototype. |

Old folders (`01_official_*`, `02_haebot_modified`, `03_one_finger_test`, `04_forearm_servo_bed`, `04_jinie_branding`, `src`, `renders`)
were removed on 2026-11-13 to stop the confusion. They are still in git history (last version: commit `4d52bfb`).
The Jinie logo source files moved to [`../docs/brand/`](../docs/brand/).
