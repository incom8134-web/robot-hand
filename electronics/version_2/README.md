# Electronics version 2: USB control, 12 V servos, 5 smart servos

Current plan. Pre-schematic. Values marked "not verified" in the study guide are still open.

## Idea
- A Windows PC runs Python, OpenCV and MediaPipe hand tracking and sends a few numbers per frame over **one USB cable**.
- The custom board turns them into servo commands and drives the servo bus directly. The 12 V supply and the servos are outside the board.
- The board takes two inputs: USB (5 V, data and firmware) and a 12 V DC jack. An on-board 12 V to 5 V regulator was agreed with the board developer on 2026-11-15, so the board can also run without a PC attached.
- Modes: follow the PC (mirror the hand, rock-paper-scissors) and idle (stored gestures when no PC data arrives). Idle without a PC depends on the 12 V to 5 V regulator above.

## Data path
PC (USB) > CH340C > ATmega328PB UART0 | ATmega328PB UART1 > half-duplex TTL circuit (tri-state buffer) > servo bus P1, P2 > 5 x STS3215 (IDs 1 to 5, 12 V)

The SC16IS750 and the separate Waveshare adapter were removed on 2026-11-16 (board developer's proposal). The DC jack and the servo connectors are on the board.

Correction from the board developer, 2026-11-16: **the 12 V does not travel on the servo bus. It goes from the DC jack straight to the STS3215 servos.** The USB connector is **mini-B**, not USB-C. The fuse is left out of this document for now at the user's request; the board developer will handle protection.

## Motors
Current direction (2026-11-16): **5 x STS3215, one per finger, in the forearm**, controller board in the base. Details in [dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md](dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md).

The earlier 3-servo grouping (thumb; index + middle; ring + pinky) stays possible in firmware. It makes rock, paper and scissors work, but pointing with one finger needs 5 servos.

## Files
| File | What |
|---|---|
| [dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md](dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md) | Motors, forearm size, board location, board spec for the developer |
| [dona_univ_robot_hand_2026-11-16_Sanjev_wiring_diagrams.docx](dona_univ_robot_hand_2026-11-16_Sanjev_wiring_diagrams.docx) | Wiring, block and power diagrams with explanation (English). |
| [동아대_robot_hand_2026-11-16_산지브_wiring_diagrams.docx](동아대_robot_hand_2026-11-16_산지브_wiring_diagrams.docx) | Same document in Korean |
| [dona_univ_robot_hand_2026-11-14_Sanjev_haebot_robot_hand_study_guide.docx](dona_univ_robot_hand_2026-11-14_Sanjev_haebot_robot_hand_study_guide.docx) | Browsable study guide from electronics to software, with diagrams and source links |

## Open items
- Half-duplex circuit details (buffer part, data-line pull-up) to be set by the board developer against the STS3215 manual.
- Bus logic level and speed with an ATmega328PB at 5 V (1 Mbps default) to be verified.
- **Open (2026-11-16): how 12 V leaves the board.** Does it share the servo connector (DATA, 12 V, GND, 3-pin), or is there a separate power connector with the bus connector carrying only DATA and GND? The diagrams currently draw the second option, following the board developer's 2026-11-16 message, and are marked "pinout to confirm" until he answers. Board GND and servo GND must be common either way for the half-duplex bus to work.
- 12 V path on the board: with the DC jack on the board, the copper and connectors carrying servo current must be rated for stall current (about 13.5 A for 5 servos).
- Fit of 5 STS3215 in a new forearm servo bed (check in CAD).

Version 1 (archived): [../version_1/](../version_1/)
