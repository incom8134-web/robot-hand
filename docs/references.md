# External reference repositories

These projects are **references only**. Their source is not vendored in this repo.
Follow the primary project for vision-to-hand architecture; use the others for
comparison. Local shallow clones used for this review live only on the analysis
machine (`/workspace/refs/`) and are not part of this git tree.

Our target setup: Arduino Nano + PCA9685, five EMAX ES08MA II servos, later a
Raspberry Pi running OpenCV / MediaPipe. CAD is InMoov Hand i2–derived.

Dates below are last git commits, shown in Asia/Seoul (UTC+9).

## Repositories

| Repo | Role | One-line summary | License | Last commit (Asia/Seoul) |
|---|---|---|---|---|
| [Bolofofopt/HumanoidRoboticArmVision](https://github.com/Bolofofopt/HumanoidRoboticArmVision) | **PRIMARY — follow this** | InMoov-based 7-DoF arm that mirrors a person in real time with MediaPipe on a Raspberry Pi 5, an Arduino Mega + PCA9685, and an Uno for the base stepper. | **MIT** (their software). InMoov mechanics remain **CC BY-NC 3.0**. | 2026-10-07 04:19 |
| [geigermartin/prostheticHand](https://github.com/geigermartin/prostheticHand) | Reference | InMoov i2 prosthetic with a PyQt GUI, four control modes (manual, gestures, EMG, webcam mocap via OpenCV / MediaPipe), Arduino Mega, servos on native PWM pins. | **No license file** — treat as all rights reserved. Do not copy code. InMoov parts are **CC BY-NC 3.0**. | 2023-09-20 21:31 |
| [utkarsh-jadhav-mech/InMoov_Robotic_Hand](https://github.com/utkarsh-jadhav-mech/InMoov_Robotic_Hand) | Reference | Student SolidWorks assembly of an InMoov-style tendon hand, plus a simple Uno + 5-servo wiring sketch. No firmware or vision. | README points to a LICENSE file that is **missing**. InMoov-derived CAD is **CC BY-NC 3.0**. Do not copy models. | 2026-05-08 16:42 |
| [kochlisGit/InmoovNet](https://github.com/kochlisGit/InmoovNet) | Reference | ECAI 2025 research stack: MediaPipe teleoperation plus speech-to-motion models, Arduino Nano ESP32 + PCA9685, comma-separated **proportional** finger angles. | **MIT** (their software). InMoov mechanics remain **CC BY-NC 3.0**. | 2025-08-02 19:22 |

## What we adopt from the primary

From [HumanoidRoboticArmVision](https://github.com/Bolofofopt/HumanoidRoboticArmVision)
we adopt the **architecture and method**, not the files:

1. **Split brain:** a vision computer (PC now, Raspberry Pi later) runs MediaPipe;
   a microcontroller only drives servos. The Pi must not bit-bang PWM.
2. **PCA9685 over I2C** with a **separate servo supply** and a **shared ground**.
   This matches our Nano + PCA9685 plan (Nano I2C on A4/A5, not Mega 20/21).
3. **MediaPipe joint angles** to decide finger flexion (MCP/PIP angle vs a
   threshold), not tip-to-wrist pixel distance, so camera distance does not
   fool the hand.
4. **A framed serial protocol** with a start marker and newline, sent at a
   limited rate (~10 Hz). We will simplify it for a 5-finger hand (see below).
5. **A PC debugger** (webcam + overlay, no robot required) before moving vision
   to the Pi.
6. **Adafruit PWMServoDriver**, 50 Hz for analog servos, after calibrating pulse
   limits on the ES08MA II (do not reuse their 100–500 tick range or 7 V rail).

We do **not** copy their source, BOM, or pin map. We also drop the Mega, the
Uno + CNC shield + NEMA 17 base, the DS5160 elbow, GPIO UART, and 7 V servo
power (the ES08MA II is a 4.8–6 V servo; use a 5–6 V, 3 A+ supply).

### Protocol we will implement (adapted)

Theirs is:

```
$<Base>,<Elbow>,<D1>,<D2>,<D3>,<D4>,<D5>,<Rotation>\n
```

at 115200 baud, with D1–D5 as binary 0/1. For our hand-only kit, use
**proportional angles** over USB serial to the Nano, for example:

```
$<thumb>,<index>,<middle>,<ring>,<pinky>\n
```

with each field 0–180. Keep `$` + newline framing so a truncated line is
ignored. Optionally add wrist later. This is also closer to InmoovNet’s
comma-separated angle list, which is a better classroom demo than open/closed
only.

### Bugs to fix if we follow their code

Do not port these as-is:

- **Finger order mismatch:** Python sends index, middle, ring, pinky, thumb;
  Mega firmware applies that sequence as thumb, index, middle, ring, pinky.
- **Polarity mismatch:** Python sends `1` when a finger is *open*; firmware and
  README treat `1` as *closed*.
- **UART pins:** README wires the Pi to Mega **Serial1** (pin 19 / RX1); firmware
  reads **Serial2**. Base-command encoding also disagrees between the README
  (0=left, 1=center, 2=right) and the Uno sketch comments (0=center, 1=left).
- **`moveAll()`** only pulses PCA9685 channels 0–6, but the fingers are on
  channels 10–15, so the start pose does not park the hand.
- Finger control is **binary**, which is too coarse for a “copy my hand” kit.

## License notes (for-profit edtech)

지니에듀테크 is a commercial education company. Summary:

| Work | Can we use it in paid courses / products? |
|---|---|
| HumanoidRoboticArmVision and InmoovNet **software** (MIT) | Yes, if we keep the copyright notice and license text on any substantial use or redistribution. Prefer reimplementing to our Nano protocol rather than copying files. |
| prostheticHand **software** and InMoov_Robotic_Hand **SolidWorks files** | **No**, not without written permission. No usable license grant. |
| **InMoov CAD / mechanics** (all four projects build on it) | **CC BY-NC 3.0**. Non-commercial only unless Gaël Langevin gives written permission. Their MIT (or missing) repo licenses do **not** relicense InMoov parts. This already applies to `cad/original/` and the InMoov-derived parts in `cad/prototype/` in this repo. |
| MediaPipe, OpenCV, Adafruit PWMServoDriver | Typically Apache-2.0 / BSD-style; commercial use is allowed under each project’s own terms. Confirm when we pin versions. |

Do not add these repos as git submodules and do not copy their trees into this
project. Link here, then write our own firmware and vision code.

See also [ATTRIBUTION.md](../ATTRIBUTION.md) and [LICENSE.md](../LICENSE.md).
