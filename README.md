<div align="center">

# 🤖 HAEBOT Hand i2 — Version 1

**5-finger, independently actuated, tendon-driven robotic hand**
*InMoov Hand i2 기반 · EMAX ES08MA II 서보 · Arduino Nano · 가위바위보 시연*

![Status](https://img.shields.io/badge/status-planning-blue)
![Version](https://img.shields.io/badge/version-V1-informational)
![MCU](https://img.shields.io/badge/MCU-Arduino%20Nano-00979D)
![CAD](https://img.shields.io/badge/CAD-FreeCAD-red)
![EDA](https://img.shields.io/badge/EDA-KiCad-314CB0)
![License](https://img.shields.io/badge/license-non--commercial-lightgrey)

**지니에듀테크(주) · Genie EduTech Co., Ltd. — Busan, Korea**

</div>

---

## 📌 Overview

HAEBOT Hand i2 V1 is a 3D-printed robotic hand derived from the open-source **[InMoov Hand i2](https://inmoov.fr/hand-i2/)** by Gael Langevin.
Version 1 re-engineers the servo mounting for the **EMAX ES08MA II** micro servos we already own, drives **all five fingers independently** with tendons and return elastics, and targets a repeatable **Rock / Paper / Scissors** demonstration.

> ⚠️ **Project status: PLANNING.** This repository currently contains the project plan and the implementation brief. CAD, electronics, and firmware will be added stage by stage. **No physical fit, current-draw, or endurance results exist yet** — nothing here should be read as tested.

## 🎯 V1 Goals

| # | Goal | Acceptance |
|---|---|---|
| 1 | 5 fingers, each with its own servo | T-05 independence test |
| 2 | Rock ✊ / Paper ✋ / Scissors ✌ gestures | T-06 gesture test (N reps) |
| 3 | Reproducible, documented engineering repo | Another builder can print, wire, and calibrate from the docs |
| 4 | Education-ready | Usable in physical-AI / vibe-coding courses |

## 🧩 System Architecture

```mermaid
flowchart LR
    PSU["DC Adapter<br/>7–12 V [EST]"] --> FUSE[Fuse + Reverse<br/>Polarity Protection]
    FUSE --> BUCK["Buck / BEC<br/>5–6 V"]
    BUCK --> CAP["Bulk Cap<br/>470–1000 µF [EST]"]
    CAP --> RAIL((Servo Rail))
    RAIL --> S1[Thumb] & S2[Index] & S3[Middle] & S4[Ring] & S5[Pinky]
    USB["USB / 5 V"] --> NANO[Arduino Nano]
    NANO -- "D3 · D5 · D6 · D9 · D10" --> S1 & S2 & S3 & S4 & S5
    NANO -. "Common GND" .- RAIL
    S1 & S2 & S3 & S4 & S5 -- Tendon --> FING[Fingers<br/>InMoov i2 geometry]
    FING -- Return elastic --> FING
```

| Subsystem | V1 Design | Status |
|---|---|---|
| Fingers | InMoov i2 geometry, Hall-sensor & magnet pockets removed | `PLANNED` |
| Actuation | Tendon flexion + elastic extension | `PLANNED` |
| Servos | 5 × EMAX ES08MA II, palm-mounted where feasible | `OWNED` — dims `[TBM]` |
| Servo cradle | Parametric adapter driven by `cad/parameters.yaml` + fit-test coupon | `PLANNED` |
| MCU | Arduino Nano (ATmega328P) | `PLANNED` |
| Power | Separate regulated 5–6 V servo rail, **common ground** | `PLANNED` |
| Sensors | **None in V1** (no Hall sensors, no magnets) | By design |

## 📂 Repository Structure

```
robot-hand/
├── README.md
├── ATTRIBUTION.md         # InMoov / third-party credits
├── LICENSE.md             # licensing notice (non-commercial)
├── docs/
│   └── 해봇핸드i2_프로젝트계획서_261111.docx   # Project plan (management report)
├── prompts/
│   └── 해봇핸드i2_구현프롬프트_261111.md        # Claude implementation brief
├── cad/                   # FreeCAD, STEP, STL (own parts only), drawings   — coming
├── electronics/           # KiCad schematic & project                         — coming
├── firmware/              # Arduino sketch                                    — coming
├── bom/                   # Bill of materials                                 — coming
└── tests/                 # Test record templates                             — coming
```

## 📄 Documents

| Document | Description |
|---|---|
| [📘 Project Plan (DOCX)](docs/해봇핸드i2_프로젝트계획서_261111.docx) | Objective, architecture, scope, BOM, stages, milestones, risks, acceptance tests, approval sheet |
| [🧠 Implementation Prompt (MD)](prompts/해봇핸드i2_구현프롬프트_261111.md) | Copy-ready brief for Claude to build the full engineering repo with strict no-fabrication rules |

## 🗓️ Roadmap

| Stage | Weeks `[EST]` | Work | Milestone |
|---|---|---|---|
| S1 | 1 | Source review & license audit | M1 — audit approved |
| S2 | 1–2 | Caliper measurement of ES08MA II, per-servo stall/peak current | M2 — `parameters.yaml` filled, regulator rating fixed |
| S3 | 2–3 | Servo cradle, spool, palm layout, fit coupon | M3 — T-01 pass |
| S4 | 3–4 | KiCad schematic + ERC, firmware & calibration mode | M4 — ERC clean, single servo runs |
| S5 | 4–5 | Full print & tendon assembly | M5 — T-04/T-05 pass |
| S6 | 5–6 | Acceptance tests & documentation | M6 — R/P/S demo recorded |

- [ ] S1 Source review & license audit
- [ ] S2 Measurement & power characterization
- [ ] S3 Mechanical design
- [ ] S4 Electronics & firmware
- [ ] S5 Print & assembly
- [ ] S6 Test & documentation

## 🧪 Acceptance Tests (planned — no results yet)

| ID | Test | Pass criterion |
|---|---|---|
| T-01 | Servo fit | Seats without force; play within tolerance |
| T-02 | Power rail | Stays within 5–6 V under 5-servo load |
| T-03 | Stall / peak current | Recorded per servo → regulator sized with ≥ 1.5× margin `[EST]` |
| T-04 | Finger range of motion | Full flex/extend, no tendon slip or binding |
| T-05 | Independence | No unintended motion of other fingers |
| T-06 | Gestures | R/P/S recognisable over N reps |
| T-07 | Thermal | Case temperature recorded, no shutdown |
| T-08 | Endurance | Failures logged; no claims beyond recorded N |

## 🏷️ Data Integrity Convention

Every number in this project carries one tag:

| Tag | Meaning |
|---|---|
| `[SRC]` | From a cited source |
| `[DS]` | Manufacturer datasheet nominal — still to be confirmed |
| `[EST]` | Engineering estimate, with range |
| `[TBM]` | To be measured on the physical part |

Files are labelled `PLANNED → DESIGNED → GENERATED → PRINTED → ASSEMBLED → TESTED`. Fusion 360 `.f3d` files are published **only** if exported from real Fusion 360.

## ⚡ Safety

- **Never power the servos from the Arduino Nano 5 V pin.** Use the separate regulated rail.
- Always connect **common ground** between the servo supply and the Nano.
- Keep fingers clear during calibration; servos can pinch.

## 📜 License & Attribution

- Mechanical design is derived from **InMoov Hand i2 © Gael Langevin**, released under a Creative Commons **Non-Commercial** license (exact version to be confirmed on [inmoov.fr](https://inmoov.fr/hand-i2/)).
- **Original InMoov STL files are not redistributed here** — download them from the official site.
- Only our own modified/new parts will be published, with attribution. **No commercial redistribution** of InMoov-derived parts.
- See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE.md](LICENSE.md).

## 🔗 References

1. InMoov Hand i2 — <https://inmoov.fr/hand-i2/>
2. geigermartin/prostheticHand — <https://github.com/geigermartin/prostheticHand>
3. Reference video — <https://www.youtube.com/watch?v=7KV5489rL3c>

---

<div align="center">

**지니에듀테크(주) Genie EduTech** · No.1 Education Technology Company
[jcodeedu.com](http://jcodeedu.com)

</div>
