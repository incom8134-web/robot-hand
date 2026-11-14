# HAEBOT Hand Controller v2 — power budget (final component selection)

Jinie EduTech · HAEBOT Hand i2 V1 · controller board v2 · **preliminary, not a production-approved design**
Components fixed by the project owner (2026-11-12): **TPSM41625** (6 V servo rail), **TPS56837** (5.1 V Pi rail), **TMC2209** (NEMA 17), PCA9685 @ 3.3 V, ATmega328P @ 5 V, CH340C, 2× SN74LVC1T45, TLV75533P, Mean Well 12 V 20 A+ SMPS, 7-pin locking Pi link, 4-layer ~115 × 56 mm PCB.
Every number is from a datasheet [S#] or marked **ASSUMPTION** (must be measured). Machine-readable: `power_budget.csv`; recompute: `/workspace/venv/bin/python concept/power_budget_calc.py`.

---

## 0. Result

| Rail | Made by | Loads | Typical | Worst case | Regulator load (worst) |
|---|---|---|---|---|---|
| **12 V input** | **Mean Well LRS-350-12** (12 V 29 A 348 W) → J1 XT60 → F1 20 A | everything | **3.74 A · 44.9 W** | **11.2 A · 134.6 W** (clone-servo peak case 12.8 A · 154 W) | **39 %** of SMPS (44 % clone case) |
| **6 V servo** (5.96 V) | **U3 TPSM41625** module | 6× MG996R (5 fingers + wrist) on PCA9685 CH0–CH5 | 4.2 A · 25 W | **15.0 A · 89 W** (all 6 stalled at 2.5 A) | **75 %** of the 20 A rating *at 6 V* |
| **5.1 V** | **U4 TPS56837** | Pi 5 + Camera 3 + fan + USB, ATmega, CH340C, TMC2209 I/O, LDO | 2.43 A · 12.4 W | **5.19 A · 26.5 W** (Pi at its official 5 A); 4.19 A with default USB limit | **65 %** of 8 A |
| **3.3 V** | **U9 TLV75533P** (from 5.1 V) | PCA9685, SN74LVC1T45 A-side, TMC2209 VREF, LED | 8 mA | 42 mA (incl. 30 mA allowance) | 8 % of 500 mA |
| **12 V motor** | 12 V → F2 2 A → **U5 TMC2209** | NEMA 17 17HS4401S at 1.0 A RMS | 0.39 A · 4.7 W | 1.0 A · 12 W allowance (calc. 0.69 A) | 50 % of TMC2209's 2 A RMS |
| AC side | 220 V | LRS-350-12 at ~85 % | ~53 W | ~158 W (181 W clone case) | – |

---

## 1. Loads

### 1.1 Servos — 6× TowerPro MG996R at 5.96 V
| Condition (6 V) | Value | Source |
|---|---|---|
| Idle (holding, no load) | 10 mA | TowerPro product page [S5] |
| Running | 500–900 mA | MG996R datasheet (Digikey copy) [S4] |
| **Stall** | **2.5 A** (datasheet [S4]); TowerPro's own page says 1.4 A [S5] | we design to the **higher 2.5 A** |
| Typical moving a finger tendon | **0.70 A — ASSUMPTION** (middle of the running range) | measure on the 1-finger rig |
| Clone servo start/stall peak | **3.0 A — ASSUMPTION** (many MG996R clones exceed the datasheet) | measure |

| Scenario | 6 V current |
|---|---|
| All 6 holding | 0.06 A |
| **Typical**: all 6 moving (hand mirroring) | **4.2 A** |
| Grip: 5 fingers stalled on an object + wrist moving | 5 × 2.5 + 0.7 = 13.2 A |
| **Worst**: all 6 stalled | **15.0 A** |
| Clone-peak: all 6 at 3 A | 18.0 A |

PCA9685 has 16 channels; **8 servo headers** are fitted (CH0–CH5 used, CH6–CH7 spare). Spares are **not** in the budget — with 6 MG996R stalled the rail is already at 75 % of its 6 V rating, so spares are light-duty only.

### 1.2 Raspberry Pi 5 at 5.1 V through J5 PI-LINK
| Item | Typical | Worst | Source |
|---|---|---|---|
| Pi 5 board, MediaPipe Hands | 2.0 A | 3.0 A | stress-ng 8.9–9.8 W ≈ 2.0 A [S7]; RPi recommends 5 A of which 1.6 A is USB [S6] |
| Camera Module 3 | 0.3 A | 0.3 A | **ASSUMPTION** [S8] |
| Active Cooler fan | 0.1 A | 0.1 A | **ASSUMPTION** |
| USB ports | 0 | **1.6 A** if `usb_max_current_enable=1`; **0.6 A** by default | [S6] |
| **Pi total** | **2.4 A** | **5.0 A** (official max) / 4.0 A (default) | |

### 1.3 Logic
| Ref | Part | Rail | Typ | Max | Source |
|---|---|---|---|---|---|
| U1 | ATmega328P-AU 16 MHz | 5 V (diode-OR) | 9.2 mA | 14 mA | [S9] |
| U6 | CH340C | 5 V | 7 mA | 20 mA | [S10] |
| U5 | TMC2209 VCC_IO | 5 V | 2 mA | 5 mA | [S11] |
| U7, U8 | SN74LVC1T45 ×2 | 3.3 V / 5 V | < 0.1 mA | 0.5 mA | [S12] |
| U2 | PCA9685PW | **3.3 V** | 6 mA | 10 mA | [S13] |
| LEDs, pull-ups, dividers | | | ~12 mA | ~15 mA | calculated |
| J6 spare I²C | | 5 V | 0 | 100 mA | allowance |

### 1.4 Base stepper — NEMA 17 17HS4401S via TMC2209, 12 V
Motor: 1.7 A rated, 1.5 Ω/phase [S14]. TMC2209: 2 A RMS / 2.8 A peak, R_DS(on) 0.17 Ω per FET [S11]. Set **I_RMS = 1.0 A** (59 % of motor rating → cool, ~23 N·cm holding, enough for a turntable base — validate).
The TMC2209 regulates coil RMS current directly, so 12 V draw = power / 12 V:

| | 1.0 A RMS (typ) | 1.2 A RMS (max) |
|---|---|---|
| Coil copper 2 × I² × 1.5 Ω | 3.00 W | 4.32 W |
| Driver 2 × I² × 0.34 Ω | 0.68 W | 0.98 W |
| Mechanical (slow base) | 1 W ASSUMPTION | 3 W ASSUMPTION |
| **12 V current** | **0.39 A** | 0.69 A → **1.0 A allowance** used for sizing |
Standstill current reduction (TMC2209 PDN) cuts holding power when the base is idle.

---

## 2. Regulators

### 2.1 U3 TPSM41625 — 12 V → 5.96 V servo rail [S1]
| Item | Value | Note |
|---|---|---|
| Input / output range | 4–16 V in (17 V abs. max) / 0.6–7.1 V out | 12 V OK; **input transients must stay < 17 V** (see 5.3) |
| **Current rating at 6 V** | **≈ 20 A, not 25 A** | TI Fig. 7-3: output current derates above 3.3 V (25 A → ~18 A at 7.1 V) |
| Set-point | VREF 1.1 V (R_VSEL 187 kΩ) + R_ADJ 4.42 kΩ over internal 1 kΩ → **5.962 V** | TI Table 7-2 "6.0 V" row; ±0.5 % ref |
| f_SW | 700 kHz (R_RT 30.1 kΩ), R_RAMP 187 kΩ | TI Table 7-3/7-4 for 5–7.1 V out |
| Current limit | 32 A typ open → **set −30 % (R_ILIM 78.7 kΩ) ≈ 22 A** | protects headers/traces, above the 15–18 A load |
| Efficiency (TI Fig. 6-1) | ~92 % at 4 A, ~95 % at 15 A | |
| **Loss (TI Fig. 6-2)** | **2.0 W typ / 4.3 W worst (15 A) / 5.3 W (18 A)** | |
| R_θJA | 13.8 °C/W on TI 90 × 90 mm 6-layer 2 oz; **ours ≈ 20 °C/W ASSUMPTION** (115 × 56 mm 4-layer, Pi 18 mm above) | |
| **T_J at T_A 40 °C** | typ ≈ **80 °C**; worst (15 A continuous) ≈ **126 °C** on our board (99 °C on TI's) | TI SOA (6 V, 15 A, natural convection) allows T_A ≈ 70 °C on TI's board |
| Protection | cycle-by-cycle + hiccup OCP, OVP, UVP, OTP 165 °C, PGOOD | PGOOD → MCU A2 |

**Verdict:** OK for typical (80 °C) and for short stalls. **All six servos stalled continuously is NOT thermally safe without airflow on this small board** (≈126 °C, at the 125 °C IC junction limit). Mitigations (all planned): firmware stall timeout (cut PCA /OE if the 6 V rail current/voltage indicates stall > 2 s), ≥ 30 thermal vias under the module into L2/L3/L4 copper, base fan, validation with a thermocouple (section 9).

### 2.2 U4 TPS56837 — 12 V → 5.1 V Pi rail [S2]
| Item | Value |
|---|---|
| Rating | 8 A continuous, 4.5–28 V in, synchronous (20.4 / 9.5 mΩ FETs), D-CAP3 |
| Set-point | VFB 0.6 V; R_top **75.0 kΩ** / R_bot **10.0 kΩ** → **5.100 V** (±1 % ref) |
| MODE | 30.1 kΩ → 500 kHz, current limit 9.6 A typ (valley 8–11.1 A) |
| L / C | 3.3 µH Würth 744325330 (I_sat 15 A, 5.9 mΩ); C_OUT 4 × 22 µF 25 V 1210 (TI typ 2, max 10); C_FF 150 pF |
| Load | worst 5.19 A = 65 % (4.19 A with default USB limit) |
| Efficiency / loss | 95 % / 0.65 W typ; 94 % / 1.69 W worst (TI Fig. 5-17, read ±1 % ASSUMPTION) |
| T_J | R_θJA,eff 30 °C/W (TI 4-layer EVM) → ≈ **91 °C** worst at T_A 40 °C (limit 150 °C) ✓ |

### 2.3 U9 TLV75533P — 5.1 V → 3.3 V [S3]
500 mA LDO, V_IN max 5.5 V (5.1 V +1 % OK), dropout 238 mV max. Load 8–42 mA → loss ≤ 76 mW ✓. Feeds PCA9685 VDD, SN74LVC1T45 3.3 V sides, TMC2209 VREF divider, 3V3 LED.

---

## 3. 12 V input, SMPS, fuses

| Branch | Typical | Worst |
|---|---|---|
| U3 6 V (out + loss) | 27.1 W | 93.7 W |
| U4 5.1 V (out + loss) | 13.1 W | 28.1 W |
| Stepper (TMC2209) | 4.7 W | 12.0 W (allowance) |
| LEDs, dividers, Q1 | 0.1 W | 0.7 W |
| **Total at J1** | **44.9 W → 3.74 A** | **134.6 W → 11.2 A** |
| Clone-peak case (6 × 3 A servos) | | 154 W → 12.8 A |

**SMPS: Mean Well LRS-350-12** (12 V, 29 A, 348 W, ~85 % eff., OLP 110–140 % hiccup, OVP 13.8–16.2 V, built-in fan on at 50 °C) [S15]. Worst load = 39 % (44 % clone case) → runs cool, fan rarely on. *Honest note:* an LRS-200-12 (17 A) would also cover the worst case with 66 % load; LRS-350-12 is chosen per the owner's "20 A+" requirement and leaves room for an elbow/extra servos later. Set the 115/230 V selector to **230 V** for Korea; **do not turn the V-ADJ pot above 12.0 V** (TPSM41625 max 16 V).

| Fuse | Rating | Reason |
|---|---|---|
| IEC inlet (AC) | **4 A T** (slow) 250 V | ~1.3 A AC at 158 W (no PFC); survives LRS cold-start inrush |
| **F1** main 12 V | **20 A ATM mini-blade (fast)** in Littelfuse 178.6764.0001 (30 A holder) | 11.2 A worst = 56 %, 12.8 A clone = 64 % (≤ 75 % rule). Below the SMPS OLP (32–41 A), so a board fault blows F1, not just hiccups the SMPS |
| **F2** stepper branch | **2 A time-lag SMD** | 2 × the 1.0 A allowance; protects the thin 12 V branch to the TMC2209 |
| 6 V / 5.1 V rails | **no fuse** | TPSM41625 (≈22 A set) and TPS56837 (9.6 A) current limits + hiccup protect them |

Cable SMPS → J1: **16 AWG** silicone pair (≤ 0.5 m, ~0.17 V drop at 11 A) with XT60 plug.

---

## 4. PCB copper — 4-layer stack and widths
Stack (JLCPCB 4-layer, preliminary): **L1 2 oz** signals + power pours · **L2 1 oz solid GND** · **L3 1 oz power planes** (12 V / 6 V / 5.1 V / 3.3 V islands) · **L4 2 oz** power pours + signals.
IPC-2221, ΔT = 10 °C (external k = 0.048, internal k = 0.024; IPC-2221 is very conservative for internal planes — IPC-2152 gives much smaller widths):

| Net | Current | IPC min, outer 2 oz | IPC min, inner 1 oz | **We use** |
|---|---|---|---|---|
| 12 V J1 → F1 → Q1 → U3/U4 | 11.2 A (12.8 clone) | 4.2 mm (5.1) | 22 mm | **L1 + L4 pours ≥ 6 mm each** + L3 12 V island, ≥ 16 stitching vias |
| **6 V U3 → servo headers** | **15 A (18 clone)** | **6.3 mm (8.1)** | 33 mm | **L1 + L4 pours ≥ 8 mm each** + L3 6 V island under J2; ≥ 30 vias (0.3 mm) at U3 VOUT and at J2 |
| Servo V+/GND per header pin | 2.5 A | 0.53 mm | – | 1.5 mm stubs from the pour |
| 5.1 V U4 → J5 Pi | 5.2 A | 1.5 mm | 7.6 mm | ≥ 3 mm L1 pour + L3 island |
| 12 V → F2 → TMC2209 VS | 2 A | 0.4 mm | – | 1.0 mm |
| Motor phases | 1.7 A | 0.3 mm | – | 0.8 mm |
| GND | all returns | – | – | L2 solid, plus GND fill on L1/L4, stitched every ~5 mm |
| Signals | mA | – | – | 0.2 mm; I²C/UART over unbroken L2 GND |
| Via current | 0.3 mm drill, 1 oz plating ≈ 1 A each (rule of thumb) | | | via counts above include ≥ 2× margin |

---

## 5. Connectors

| Ref | Connector | Rating | Worst current | Margin | Note |
|---|---|---|---|---|---|
| J1 | **XT60PW-M** (Amass, RA PCB) | 30 A | 11.2 A (12.8) | ✓ 37 % | polarized, locking-ish, hobby-standard; LCSC C98732 |
| J2 | 3 × 8 2.54 mm servo header | ~3 A/pin (typical gold header) | 2.5 A per MG996R | ⚠ **83 %** | the servo's own JR/Futaba plug is the real limit; validate temperature at stall |
| **J5 PI-LINK** (7-pin locking) | see 5.1 | | 5.2 A on **2 × 5.1 V pins** = 2.6 A/pin; 3 GND pins = 1.7 A/pin | | |
| J3 | JST XH 4P side-entry (motor) | 3 A/pin (AWG 22) [S16] | 1.7 A peak | ✓ | |
| J4 | JST XH 3P side-entry (limit) | 3 A | mA | ✓ | |
| J6 | JST XH 4P side-entry (I²C 5 V) | 3 A | 0.1 A | ✓ | |
| J8 | USB-C (CH340C only) | – | < 50 mA | ✓ | VBUS only feeds the MCU via diode-OR, never the Pi or servos |

### 5.1 7-pin Pi link candidates (owner: "connector TBD")
| Candidate | Pitch | Current/pin | 2 × 5.1 V pins carry | Lock | Verdict |
|---|---|---|---|---|---|
| JST PH 7P | 2.0 mm | 2 A | 4 A < 5.2 A | friction | ✗ too weak |
| JST XH 7P | 2.5 mm | 3 A (AWG 22) | 6 A → 87 % at 5.2 A | friction "lock" | ⚠ OK only with default 0.6 A USB (4.2 A = 70 %) |
| **Molex Micro-Fit 3.0 1×7** (43650-0713 RA, mating 43645-0700) | 3.0 mm | **5 A** (up to 8.5 A with 18 AWG per Molex) | 10 A → 52 % | **positive latch** | **✓ recommended.** LCSC C17338151 exists but showed out of stock → buy via Digikey/Mouser or JLC global sourcing |
Pin-out (board side): 1 = 5V1, 2 = 5V1, 3 = GND, 4 = GND, 5 = GND, 6 = TXD→Pi (Pi pin 10), 7 = RXD←Pi (Pi pin 8).
**Pi side is the weak point:** the Pi end is a 2 × 7 Dupont housing on GPIO pins 1–14 (5 V = pins 2, 4; GND = 6, 9, 14; UART = 8, 10). Raspberry Pi does not publish a current rating for the header's 5 V pins and Dupont crimps vary (1–3 A). At 5.2 A that is 2.6 A per contact → **validate** (section 9). Use 20 AWG for the 5 V/GND wires (Micro-Fit accepts 18–24 AWG; Dupont max ~22 AWG — use 22 AWG at the Pi end), cable ≤ 100 mm. Drop at 5 A ≈ 0.12 V → Pi sees ≈ 4.98 V.
**MCU reset / GPIO4 line was dropped** in the 7-pin plan. Consequence: the Pi can talk to the ATmega but **cannot reflash it** (no auto-reset). Options: (a) flash over USB-C/CH340 (auto-reset via DTR — kept on the board); (b) **recommended for a classroom:** use the 8-pin Micro-Fit 1×8 (43650-0813) and add GPIO4 → 2N7002 → RESET so the Pi can update firmware with `avrdude`.

---

## 6. Capacitors
| Location | Value | Why |
|---|---|---|
| 12 V input bulk (C1, C2) | **2 × 470 µF 35 V** low-ESR electrolytic (CapXon, Ø10 × 10.5 mm) | holds 12 V during 0 → 15 A servo steps (≈ 7.9 A step at 12 V): ΔV ≈ I·t/C = 7.9 A × 100 µs / 940 µF ≈ 0.8 V while the SMPS loop responds; also damps XT60 hot-plug ringing (key for the 17 V TPSM41625 limit). 35 V because the TVS clamp is ~21.5 V |
| U3 TPSM41625 input | **4 × 22 µF 25 V X7R 1210** (= 88 µF, TI minimum) + **100 µF 50 V hybrid polymer** (Panasonic EEHZA1H101P, TI Table 7-10) | TI requirement; the hybrid cap is TI's recommended bulk for load transients |
| U3 output | **6 × 47 µF 10 V X7R 1210** at the module (TI: 134 µF effective minimum for 5–7.1 V at 12 V in = 6 × 47 µF after DC bias) | stability |
| 6 V servo bulk at J2 | **2 × 470 µF 35 V** electrolytic (same part as C1/C2) | local reservoir for servo start currents; ESR damps header/cable ringing. Transient: ΔV ≈ ΔI/(2π·f_c·C) ≈ 15 A/(2π·~50 kHz·~1 mF) ≈ 50 mV — **confirm with TI WEBENCH / bench step test** |
| U4 TPS56837 | in: 2 × 22 µF 25 V 1210 + 100 nF; out: 4 × 22 µF 25 V 1210 (≈ 50 µF effective at 5 V); C_FF 150 pF; C_SS 47 nF; C_BOOT 100 nF | TI Table 7-2 (500 kHz, 5 V row) |
| U5 TMC2209 VS | 100 µF 50 V hybrid polymer + 100 nF; charge pump 22 nF (CPO–CPI) + 100 nF (VCP); 5VOUT 2.2 µF + 100 nF | TMC2209 datasheet application circuit |
| U9 LDO | 1 µF in / 1 µF out (TLV755P stable with 1 µF) | |
| Every IC | 100 nF X7R at each supply pin | decoupling |

---

## 7. Logic-level interfaces (I²C and UART)
- **I²C (ATmega 5 V ↔ PCA9685 3.3 V): no level shifter needed.** PCA9685 SDA/SCL (and all its inputs) are **5.5 V tolerant** even at VDD = 3.3 V [S13]. So the bus is pulled up to **5 V** (4.7 kΩ to the MCU 5 V): ATmega V_IH = 0.6 × V_CC = 3.0 V is met with full margin, and PCA9685 V_IH = 0.7 × 3.3 = 2.31 V is also met. Pulling up to 3.3 V instead would leave only 0.3 V margin at the ATmega — rejected. J6 spare I²C is therefore a 5 V I²C port.
- **PCA9685 /OE** driven by ATmega D7 (5 V) into a 5.5 V-tolerant input; 10 kΩ pull-up to 3.3 V keeps servos disabled at boot.
- **PCA9685 → servo signals are 3.3 V PWM.** MG996R accepts 3.3 V logic in common use, but TowerPro does not specify V_IH → **validate**; fallback: 74AHCT125 buffer to 5 V (not fitted).
- **UART:** U7 SN74LVC1T45 (V_CCA 3.3 V, V_CCB 5 V, DIR = A→B): Pi TXD → MCU RXD. U8 SN74LVC1T45 (V_CCA 5 V, V_CCB 3.3 V, DIR = A→B): MCU TXD → Pi RXD. I_off feature keeps both safe when the Pi is unplugged; 100 kΩ pull-up holds the Pi-TX line idle-high. SW2 selects Pi or USB (CH340C).

---

## 8. Heat on the board
| Part | Typical | Worst |
|---|---|---|
| U3 TPSM41625 | 2.0 W | 4.3 W (5.3 W clone) |
| U4 TPS56837 + L | 0.65 W | 1.7 W |
| U5 TMC2209 | 0.68 W | 0.98 W |
| Q1 reverse-polarity P-FET (5 mΩ) | 0.07 W | 0.62 W |
| U9 LDO, LEDs, misc | 0.1 W | 0.15 W |
| **Board total** | **≈ 3.5 W** | **≈ 7.8 W** (≈ 8.8 W clone) |
Typical: passive is fine. Worst: the 18 mm gap under the Pi + case vents + **base fan** are required.

---

## 9. Validation still required before JLCPCB (owner's list)
| # | Item | Why it is open | How to validate | Pass criterion |
|---|---|---|---|---|
| 1 | **Regulator thermal** (TPSM41625, TPS56837) | TI thermal data is for larger 6-layer / EVM boards; our 4-layer board has the Pi 18 mm above. Worst-case estimate 126 °C for the TPSM41625 at 15 A continuous | build the power section first (or the TI EVMs), run 15 A electronic load at 6 V and 5 A at 5.1 V inside the case with the Pi on top; thermocouple/IR on module case | TPSM41625 case < 100 °C at 15 A for 60 s and < 85 °C at typical; TPS56837 < 90 °C at 5 A; then set firmware stall timeout |
| 2 | **TMC2209 motor current** | onboard TMC2209 at 1.0 A RMS for a 1.7 A motor; base torque need unknown; TMC2209 practical limit ~1.4 A RMS without heatsink | measure base torque requirement; run at 1.0/1.2 A RMS 30 min | driver < 90 °C, no missed steps at max base speed/load |
| 3 | **Servo peak loads** | MG996R stall 2.5 A (datasheet) vs 1.4 A (TowerPro) vs clones ~3 A; tendon loads unknown | current probe on 1 servo: start, move, grip, stall; then all 6 | single-servo peak ≤ 3 A; 6-servo peak ≤ 18 A; 6 V rail dip < 0.3 V |
| 4 | **7-pin connector rating** | Micro-Fit is fine (5 A/pin); the **Pi header 5 V pins + Dupont crimps** are unrated | 5 A load through the finished cable for 30 min, measure ΔT and voltage drop at the Pi pins | ΔT < 20 °C, Pi pin 2 ≥ 4.9 V; otherwise keep USB limit at 0.6 A |
| 5 | **PCB fit** | 115 × 56 mm must hold the 11 × 16 mm module + 14 large caps + XT60 under/around the Pi; heights under the Pi ≤ 12 mm; Pi mounting holes | full KiCad placement + 3D check with Pi 5 STEP and case | no part > 12 mm under the Pi, 2.6 mm keep-out around M2.5 holes, connectors reachable |
| 6 | 12 V transient vs TPSM41625 17 V abs. max | TVS (SMBJ13A) clamps ~21.5 V at full surge current | scope J1 on XT60 hot-plug with 0.5 m cable | peak < 16 V (else add RC snubber / switch AC side only) |

---

## 10. Answers for seniors
**Q1. Why one 12 V supply?** The NEMA 17 needs it (TMC2209 VS 4.75–29 V, higher V = faster steps), 12 V is the industrial-standard SMPS voltage, and current in the cable is halved vs 6 V (135 W = 11 A at 12 V vs 27 A at 5 V). Local regulators make each exact voltage at the load.

**Q2. Why separate 6 V and 5.1 V rails?** Six MG996R can pull 15 A when stalled and are electrically noisy brushed motors. On a shared rail the Pi would brown out mid-demo. Separate regulators isolate them; servos get 6 V for full torque (11 kg·cm vs 9.4 at 4.8 V), the Pi gets exactly 5.1 V.

**Q3. Why not one big 5 V supply?** Servos lose ~15 % torque at 5 V, a 5 V rail would need ~20 A, a stall would reset the Pi, and the stepper still needs 12 V.

**Q4. Why TPSM41625 for the servos?** One part does 20 A at 6 V with integrated inductor and FETs (no external inductor/diode to size), ~95 % efficient at 15 A, full protection (OCP hiccup, OVP, UVP, OTP, PGOOD), adjustable current limit, and room for growth. Trade-offs: it is rated **20 A at 6 V, not 25 A** (TI derating), it is a fine-pitch 69-pin QFN that needs JLCPCB assembly (not hand-solderable), and its input is limited to 16 V.

**Q5. Why TPS56837 for the Pi?** 8 A synchronous buck (~95 %), only ~12 small parts, 3 × 3 mm, D-CAP3 fast transient response for the Pi's load steps, 65 % load at the Pi's full 5 A — cool and with margin.

**Q6. What happens when servos stall?** Each stalled MG996R draws ~2.5 A; all six = 15 A, still inside the TPSM41625's 20 A rating. Above ~22 A (short, jammed hand) the module current-limits and hiccups; the Pi is unaffected (own regulator). Firmware: ramp moves, stagger starts, watch PGOOD (A2) and 6 V sense (A1), cut all servos with PCA9685 /OE (D7) after a stall timeout. A stalled servo also overheats itself — the firmware must not keep pushing a finger into an object.

**Q7. Why TMC2209 instead of A4988, and why on-board / standalone?** Silent StealthChop (classroom!), 256-µstep interpolation, lower losses, standstill current reduction. **On-board IC** (not a StepStick socket): JLCPCB assembles it, its thermal pad sinks into the 4-layer planes (a StepStick module is thermally limited and can be plugged in backwards), and the board stays flat and professional. **Standalone STEP/DIR/EN with fixed config** (MS1 = H, MS2 = L → 1/16 step interpolated to 1/256; SPREAD = L → StealthChop; VREF divider → 1.0 A RMS): simplest for students, no software needed to make the motor safe. An optional single-wire **UART** (JP1 solder jumper, 1 kΩ to D8, SoftwareSerial + TMCStepper library) is available for teaching current/StallGuard later.

**Q8. Is the I²C between a 5 V MCU and a 3.3 V PCA9685 safe?** Yes: PCA9685 inputs are 5.5 V tolerant, so the bus is pulled up to 5 V and both sides see valid levels; no shifter needed.

**Q9. Protection chain?** AC: IEC inlet with 4 A T fuse + switch → LRS-350-12 (OLP hiccup, OVP 13.8–16.2 V, OTP) → J1 XT60 → **F1 20 A** → **Q1 P-MOSFET** (reverse polarity + soft power switch SW1) → **D1 SMBJ13A TVS** + 940 µF bulk → 12 V rail → (a) **F2 2 A** → TMC2209 (own OCP/short-to-GND/OTP) → motor; (b) **TPSM41625** (≈22 A limit, OVP, OTP) → 6 V servos; (c) **TPS56837** (9.6 A limit, OVP/UVP/OTP) → 5.1 V Pi + logic → **TLV75533P** (foldback limit, OTP) → 3.3 V. USB-C VBUS only reaches the MCU through a diode-OR.

**Q10. What about the Pi's "5 A" and usb_max_current_enable?** The 5.1 V rail can supply 8 A, so the regulator is not the limit any more — the Pi header pins and cable are. Default: **leave the Pi at its 600 mA USB limit** (Pi ≤ 4 A). Only if USB devices need more, set `usb_max_current_enable=1` in `/boot/firmware/config.txt` **after** validation item 4 passes. (`PSU_MAX_CURRENT=5000` in the EEPROM does the same at boot level.) Never connect the Pi's own USB-C supply at the same time.

**Q11. How sure are the numbers?** Datasheet values are cited. Assumptions: servo running current under tendon load (0.7 A), clone peak (3 A), camera (0.3 A), fan (0.1 A), stepper mechanical power, our board's thermal resistance (20 °C/W) and the TPS56837 efficiency read from a graph. Even with all servo numbers at the 3 A clone peak the SMPS is at 44 % and F1 at 64 %.

---

## Sources
- [S1] TI TPSM41625 datasheet (Rev. A) — https://www.ti.com/lit/ds/symlink/tpsm41625.pdf (Fig. 6-1/6-2/6-6/6-7 efficiency, loss, SOA; Fig. 7-3 current vs V_OUT; Tables 7-1..7-4, 7-10..7-12). LCSC C5219357 (TPSM41625MOVR).
- [S2] TI TPS5683x datasheet SLVSGM3B — https://www.ti.com/lit/ds/symlink/tps56837.pdf (Table 6-1 MODE, Table 7-2 components, R_θJA). LCSC C22428366.
- [S3] TI TLV755P datasheet — https://www.ti.com/lit/ds/symlink/tlv755p.pdf. LCSC C404027.
- [S4] MG996R datasheet (Digikey copy): running 500–900 mA, stall 2.5 A at 6 V — https://media.digikey.com/pdf/Data%20Sheets/Terasic%20Technologies/MG996R.pdf
- [S5] TowerPro MG996R page: idle 10 mA, no-load 170 mA, stall 1.4 A, 4.8–6.6 V — https://towerpro.com.tw/product/mg996r/
- [S6] Raspberry Pi documentation, power supplies (Pi 5: 5 A recommended, USB 1.6 A / 600 mA) — https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/power-supplies.adoc
- [S7] Permacomputing wiki, SBC power consumption (Pi 5 stress-ng 8.9–9.8 W) — https://permacomputing.net/SBC_power_consumption/
- [S8] Camera Module 3 current: no official figure — ASSUMPTION.
- [S9] Microchip ATmega328P datasheet — https://docs.arduino.cc/resources/datasheets/ATmega328P-datasheet.pdf
- [S10] WCH CH340C datasheet (ICC 7–20 mA).
- [S11] ADI/Trinamic TMC2209 datasheet rev 1.09 — https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_Datasheet_rev1.09.pdf (2 A RMS, 2.8 A peak, R_DS(on) 0.17 Ω, I_RMS = 325 mV/(R_S+20 mΩ)·V_REF/2.5 V/√2, standalone MS1/MS2). LCSC C2150710.
- [S12] TI SN74LVC1T45 datasheet — https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf. LCSC C7843.
- [S13] NXP PCA9685 datasheet (5.5 V tolerant inputs, IDD 6–10 mA) — https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf
- [S14] 17HS4401S datasheet (Handson Technology): 1.7 A, 1.5 Ω — https://www.handsontec.com/dataspecs/17HS4401S.pdf
- [S15] Mean Well LRS-350-12: 29 A / 348 W, OLP 110–140 % hiccup, fan on at 50 °C — https://www.meanwells.com/products/mean-well-lrs-350-series-power-supply-lrs-350-12 ; datasheet https://www.mean-well.ru/uploads/files/datasheets/LRS-350-12.pdf
- [S16] JST XH datasheet (3 A with AWG 22) — https://www.jst.com/wp-content/uploads/2025/06/eXH.pdf
- [S17] Molex Micro-Fit 3.0 43650-0713 — https://www.molex.com/en-us/products/part-detail/436500713 ; LCSC C17338151 (out of stock at time of check).
- [S18] IPC-2221 conductor sizing: I = k·ΔT^0.44·A^0.725 (k = 0.048 external, 0.024 internal).
