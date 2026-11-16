# HAEBOT hand: design decisions (2026-11-16)

Update 2026-11-16: no Waveshare adapter and no SC16IS750. ATmega328PB with half-duplex TTL servo bus, 12 V input on the board (see the EN and KO docs).

Status: direction agreed in chat, not yet checked in CAD. Sizes marked "estimate" come from the STS3215 box dimensions and the InMoov i2 STL files in `cad/original/`.

## Motors
- **5 x Feetech STS3215 (12 V), one per finger.** Firmware can still group fingers (for example index + middle) to act like 3 servos. Three servos can never point with one finger.
- STS3215 body: 45.22 x 24.7 x 35 mm (box label).
- **Do not put them in the palm.** The stock `i2_WristLargeV2` is 112.6 mm wide. Five servos side by side need about 124 mm (5 x 24.7). The hand covers are about 16 mm thick (from STL sizes). The InMoov servo parts were drawn for the slimmer JX PDI-6225MG, so a new servo bed is also needed.
- **Motors go in the forearm.** New 5-servo bed and 5 new pulleys are to be designed. The stock `RobServoBedV6` (66.7 x 111.6 x 39.7 mm) is too small.

## Forearm servo section (estimate)
- Servos staggered along the arm in 2 columns (3 + 2), long side along the arm.
- Cross-section about 52 x 45 mm including pulleys. Inside diameter about 75 mm, **outer diameter about 85 mm, length about 150 mm**.
- Hand stays standard InMoov i2 size (palm about 92 mm wide).

## Board and power
- **Controller board goes in the base**, not the arm. Easier to build and debug; no packing needed.
- Only the 3-wire servo bus and the 12 V wire go up the arm.
- Servo power: external 12 V supply with a barrel jack, fuse and switch on a separate small panel in the base. No buck converter (STS3215 runs from 12 V, control is USB only). Assumed, not confirmed by the user.
- The 12 V supply is external. The 12 V input, fuse and servo connectors P1, P2 are on the board (updated from the earlier separate-adapter plan).

## Board spec for the board developer (base mounting)
| Item | Value |
|---|---|
| Size | 80 x 50 mm target, 100 x 60 mm maximum |
| Layers / thickness | 2 layers, 1.6 mm |
| Mounting | 4 x M3 holes, 4 mm in from corners |
| Parts | Top side. Height not limited |
| Add | Reset button, LEDs (power, USB, bus), test points (5 V, 3.3 V, GND, TX, RX, SPI), debug header, locking connector for the servo bus out |
| Connectors | USB-C on one short edge, 3-pin servo bus (Data, V+, GND) on the opposite edge |

If the board is later moved into the arm: target 55 x 25 mm, maximum 60 x 30 mm, height under 12 mm.

## Open
- Confirm the forearm and servo bed fit in CAD.
- USB connector type (C or B) pending.
