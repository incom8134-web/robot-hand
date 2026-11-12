# HAEBOT Hand Controller — v2 (final component selection, preliminary layout)

Jinie EduTech · HAEBOT Hand i2 V1 · custom controller board that carries a Raspberry Pi 5 on top.
**Status: concept / pre-schematic. Component selection is fixed. The BOM is NOT production-approved.
See "Validation still required before JLCPCB" in [power_budget.md](power_budget.md#9-validation-still-required-before-jlcpcb-owners-list).**
v1 (A4988, Pololu buck modules, screw terminal) is archived in [`archive_v1/`](archive_v1/).

## What the board does
- The **Raspberry Pi 5** runs MediaPipe hand tracking and sends joint targets over UART.
- The **ATmega328P** (5 V, Arduino-compatible) turns those targets into:
  - I²C commands to the **PCA9685**, which drives 6× MG996R servos (5 fingers + wrist);
  - STEP/DIR to the **TMC2209**, which drives the NEMA 17 base.
- A single **12 V Mean Well LRS-350-12** powers everything:
  - **TPSM41625** → 6 V servo rail;
  - **TPS56837** → 5.1 V for the Pi and logic;
  - **TLV75533P** → 3.3 V;
  - the TMC2209 runs straight from 12 V through a 2 A fuse.

## Fixed component selection
| Function | Part | Notes |
|---|---|---|
| Pi 5 rail | **TPS56837** 12 V → 5.10 V, 8 A | worst 5.2 A (65 %), 500 kHz, 3.3 µH |
| Servo rail | **TPSM41625** module 12 V → 5.96 V | ⚠ rated **≈20 A at 6 V** (TI derating), not 25 A. Worst load 15 A (75 %). One rail for all 6 MG996R |
| Stepper | **TMC2209** onboard QFN, **standalone** (STEP/DIR/EN), 12 V | 1.0 A RMS for the 17HS4401S, StealthChop, 1/16 → 1/256. Optional UART via solder jumper JP1 |
| Servo PWM | **PCA9685** at 3.3 V | inputs 5.5 V-tolerant → **no I²C level shifter**; I²C pulled up to 5 V |
| MCU | **ATmega328P-AU** at 5 V, 16 MHz | diode-OR supply (5.1 V rail or USB) |
| USB-UART | **CH340C** | USB-C, auto-reset (DTR) |
| Pi UART levels | **2× SN74LVC1T45** | one per direction (U7 Pi→MCU, U8 MCU→Pi) |
| 3.3 V | **TLV75533P** LDO from 5.1 V | 42 mA worst of 500 mA |
| Supply | **Mean Well LRS-350-12** (12 V 29 A) + IEC inlet (4 A T) | worst 11.2 A = 39 % |
| Pi link | **J5 7-pin locking**: 2× 5.1 V, 3× GND, TX, RX | recommended **Molex Micro-Fit 3.0** 43650-0713 (5 A/pin). The reset line was dropped; see power_budget.md §5.1 for the 8-pin option |
| PCB | 4-layer, 115 × 56 mm (preliminary) | L1 2 oz / L2 GND / L3 power / L4 2 oz |

**TMC2209 choice: onboard IC + standalone mode.**
- **Onboard IC:** JLCPCB assembles it, its thermal pad goes into the 4-layer planes, and there is no socket to insert backwards.
- **Standalone mode:** current and microstepping are fixed by resistors, so the motor is safe without any firmware setup, which suits students.
- **UART option:** close JP1 to teach UART current/StallGuard later.

## Key numbers (from [power_budget.md](power_budget.md) / [power_budget.csv](power_budget.csv))
| | Typical | Worst |
|---|---|---|
| 6 V servo rail | 4.2 A · 25 W | **15.0 A · 89 W** (all six stalled at 2.5 A). Clone peak 18 A |
| 5.1 V Pi rail | 2.43 A · 12.4 W | **5.19 A · 26.5 W**. 4.19 A with the default Pi USB limit |
| 3.3 V | 8 mA | 42 mA |
| Stepper (12 V) | 0.39 A | 1.0 A allowance |
| **12 V input** | **3.74 A · 44.9 W** | **11.2 A · 134.6 W**. Clone case 12.8 A · 154 W |
| SMPS | LRS-350-12, 29 A | 39 % load (44 % clone case) |
| Fuses | AC 4 A T · **F1 20 A** blade · **F2 2 A** slow (TMC branch) | |
| Board heat | ≈ 3.5 W | ≈ 7.8 W |

## Drawings (all generated from `concept/`)
| File | What |
|---|---|
| [renders/wiring_back_colorcoded.png](renders/wiring_back_colorcoded.png) | **BOTTOM view (mirrored)**, colour-coded nets, every part with ref + name + purpose (side tables) |
| [renders/power_tree_v2.png](renders/power_tree_v2.png) | power tree, amps and watts per branch |
| [renders/layout_top.png](renders/layout_top.png) | to-scale top view, real package sizes, Pi outline |
| [renders/3d_top.png](renders/3d_top.png), [3d_iso_no_pi.png](renders/3d_iso_no_pi.png), [3d_iso_with_pi.png](renders/3d_iso_with_pi.png) | 3D mock-up with callouts |
| [HAEBOT_HandController_v2_concept.step](HAEBOT_HandController_v2_concept.step) | light STEP of the board (no silkscreen text) |
| [HAEBOT_HandController_v2_concept_STEP_full.zip](HAEBOT_HandController_v2_concept_STEP_full.zip) | full STEP with silkscreen, and board + Pi 5 + standoffs + PI-LINK cable |

Net colours: 12 V red · 6 V orange · 5.1 V yellow · 3.3 V gold · GND green hatched · I²C blue · UART purple · stepper cyan · USB magenta · other grey.

**Regenerate** (needs the repo venv with cadquery):
```
cd electronics/concept
/workspace/venv/bin/python power_budget_calc.py   # -> ../power_budget.csv + printed summary
/workspace/venv/bin/python layout.py              # placement sanity check (overlap / holes / height <= 12 mm under the Pi)
/workspace/venv/bin/python draw_2d.py             # layout_top, wiring_back_colorcoded, power_tree_v2
/workspace/venv/bin/python model_3d.py            # STEP + 3D renders
```

## Board zones
- **Open zone (x 0–30 mm, not under the Pi):**
  - J1 XT60 12 V in, F1 20 A blade fuse, Q1 reverse-polarity P-FET, D1 TVS;
  - C1/C2 12 V bulk;
  - SW1 power switch;
  - J2 servo headers (3×8): CH0 thumb … CH4 pinky, CH5 wrist, CH6–7 spare;
  - status LEDs, logo.
- **Under the Pi (x 30–115 mm, ≤ 12 mm tall):**
  - U3 TPSM41625 with its capacitors, plus C14/C15 6 V reservoir;
  - U2 PCA9685;
  - U5 TMC2209 with F2 and C47;
  - U4 TPS56837 with L1;
  - U1 ATmega328P, U6 CH340C, U7/U8 translators, U9 LDO;
  - J3 motor, J4 limit, J5 PI-LINK and J6 I²C on the top edge;
  - J8 USB-C, SW2 serial select and SW3 reset on the right edge.

## MCU pin map (preliminary)
| Pin | Use |
|---|---|
| D0/D1 | UART: RX via SW2 (Pi U7 or CH340C), TX to U8 and CH340C |
| A4/A5 | I²C to PCA9685 and J6 (4.7 k to 5 V) |
| D2 / D3 / D4 | TMC2209 STEP / DIR / EN (ENN, 10 k pull-up = disabled) |
| D5 | limit switch J4 |
| D6 | TMC2209 DIAG |
| D7 | PCA9685 /OE (10 k pull-up = servos off at boot) |
| D8 | TMC2209 PDN_UART via JP1 + 1 k (optional) |
| D13 | STAT LED |
| A0 / A1 | 12 V sense (47k/10k) / 6 V sense (10k/10k) |
| A2 / A3 | TPSM41625 PGOOD / TPS56837 PG |

## Raspberry Pi settings
- Enable the UART: `enable_uart=1` and `dtparam=uart0=on`. Use `/dev/serial0` on GPIO14/15 (pins 8/10). Disable the serial console.
- **USB current (`usb_max_current_enable` / `PSU_MAX_CURRENT`):**
  - The 5.1 V rail can deliver 8 A, so the regulator is no longer the limit. The limit is now J5 and the Pi header 5 V pins.
  - **Default: leave the Pi at its 600 mA USB limit**, giving a Pi total of ≤ 4 A.
  - Only after validation item 4 passes (5 A through the cable for 30 min, ΔT < 20 °C, ≥ 4.9 V at the Pi) may you set `usb_max_current_enable=1` in `/boot/firmware/config.txt`, or `PSU_MAX_CURRENT=5000` in the EEPROM.
  - Never plug the Pi's own USB-C supply in at the same time as J5.

## Honest open issues (also in power_budget.md §9)
1. **TPSM41625 at 6 V:**
   - It is rated ≈20 A, not 25 A.
   - Six servos stalled continuously (15 A) is thermally marginal on this small board under the Pi: estimated T_J ≈ 126 °C (ASSUMPTION 20 °C/W).
   - Needs a firmware stall timeout, thermal vias, airflow and bench validation.
2. **Input transients vs 17 V abs. max:**
   - The TPSM41625 PVIN absolute maximum is 17 V, but the SMBJ13A clamps at ~21.5 V at full surge current.
   - Keep the LRS output at 12.0 V, don't hot-plug, and scope it (validation item 6).
3. **Servo headers:** 2.54 mm header pins (~3 A) carry up to 2.5 A at stall, which is 83 %.
4. **Pi link current:** the Pi header 5 V pins and Dupont crimps are unrated at 5 A.
5. **Servo signal level:** the PCA9685 sends 3.3 V PWM into the MG996R signal input. This usually works but is not specified. Fallback: a 74AHCT buffer.
6. **MG996R clone variation:** clones may exceed the 2.5 A datasheet stall current (budgeted as an 18 A case).
7. **Supply size and noise:** the LRS-350-12 has a fan and measures 215 × 115 × 30 mm. Check that it fits in the base. An LRS-200-12 would also work electrically.
8. **Stock and unverified parts:**
   - Molex 43650-0713 and the 470 µF CapXon are out of stock at LCSC, and the 0.11 Ω sense resistor listing is out of stock. Pick equivalents before ordering.
   - Several E96 resistors are listed as LCSC "TBD".
9. **Pi cannot reflash the MCU:** the reset line was dropped from the 7-pin link. Use USB-C/CH340C for firmware, or switch to the 8-pin Micro-Fit option.
10. **Layout is not yet a real PCB:** the placement is a concept. Do the KiCad schematic, layout and DRC before JLCPCB.

## Files
- `power_budget.md` — full power, thermal, fuse, copper, connector and capacitor analysis, the senior FAQ, the validation list and sources.
- `power_budget.csv` and `concept/power_budget_calc.py` — the numbers and the script that computes them.
- `bom_controller_v2.csv` — every line has ref, value, MPN, package, LCSC# (verified by search, otherwise "TBD"), qty, rail and purpose.
- `concept/layout.py` (placement, the single source of truth), `concept/draw_2d.py`, `concept/model_3d.py`.
- `archive_v1/` — the previous v1 concept (README_v1, BOM v1, STEP, renders, scripts). The archived scripts are kept for reference and are not maintained.
